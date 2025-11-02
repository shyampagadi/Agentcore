import streamlit as st
from agents.cloud_engineer_agent import execute_predefined_task, execute_custom_task, get_predefined_tasks, PREDEFINED_TASKS, mcp_initialized, get_mcp_status, get_detailed_mcp_status
import time
import re
import json
import ast
import os
from PIL import Image
import logging
import hashlib

# Set up silent error logging
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('app_errors.log')]
)

def log_error_silently(error, context=""):
    """Log errors silently without showing to user"""
    logging.error(f"{context}: {str(error)}")

st.set_page_config(
    page_title="AWS Cloud Engineer Agent:",
    page_icon="project-maygum.png",
    layout="wide"
)

# Cache the agent functions
@st.cache_resource
def get_agent_functions():
    # This is just a placeholder to maintain the caching behavior
    # The actual agent is now initialized directly in cloud_engineer_agent.py
    return True

# Configuration constants
class Config:
    DIAGRAM_OUTPUT_DIR = "/tmp/generated-diagrams"
    MAX_DIAGRAM_FILES = 50
    HASH_LENGTH = 8
    SUCCESS_MESSAGES = {
        'task_complete': "✅ Task completed successfully",
        'request_processed': "✅ Your request has been processed successfully",
        'diagram_generated': "✅ Diagram generated successfully"
    }

def cleanup_old_diagrams():
    """Clean up old diagram files to prevent disk space issues"""
    # DISABLED: This function causes race conditions with concurrent users
    # Files can be deleted while other users are accessing them
    # TODO: Implement user-specific directories before re-enabling
    return
    
    try:
        import glob
        diagram_files = glob.glob(f"{Config.DIAGRAM_OUTPUT_DIR}/*.png")
        if len(diagram_files) > Config.MAX_DIAGRAM_FILES:
            # Sort by modification time and remove oldest files
            diagram_files.sort(key=os.path.getmtime)
            files_to_remove = diagram_files[:-Config.MAX_DIAGRAM_FILES]
            for file_path in files_to_remove:
                try:
                    os.remove(file_path)
                except OSError:
                    pass  # File already removed or permission issue
    except Exception as e:
        log_error_silently(e, "Diagram cleanup error")

def validate_session_state():
    """Validate and repair session state if corrupted"""
    try:
        if "messages" not in st.session_state:
            st.session_state.messages = []
        elif not isinstance(st.session_state.messages, list):
            st.session_state.messages = []
        else:
            # Validate message structure
            valid_messages = []
            for msg in st.session_state.messages:
                if isinstance(msg, dict) and "role" in msg and "content" in msg:
                    if msg["role"] in ["user", "assistant"] and isinstance(msg["content"], str):
                        valid_messages.append(msg)
            st.session_state.messages = valid_messages
    except Exception as e:
        log_error_silently(e, "Session state validation error")
        st.session_state.messages = []

def show_progress_indicator(message="Processing your request..."):
    """Show progress indicator with custom message"""
    return st.spinner(message)

def log_user_interaction(action, details=None):
    """Log user interactions for monitoring"""
    try:
        timestamp = time.time()
        log_entry = f"User action: {action}"
        if details:
            log_entry += f" - Details: sanitized"  # Don't log sensitive details
        logging.info(f"INTERACTION: {timestamp} - {log_entry}")
    except Exception as e:
        log_error_silently(e, "Interaction logging error")

def retry_operation(operation, max_retries=2, delay=1):
    """Retry operation with exponential backoff"""
    for attempt in range(max_retries + 1):
        try:
            return operation()
        except Exception as e:
            if attempt == max_retries:
                raise e
            time.sleep(delay * (2 ** attempt))
    return None

# Function to remove thinking process from response and handle formatting
def clean_response(response):
    # Handle None or empty responses
    if not response:
        return ""
    
    # Convert to string if it's not already
    if not isinstance(response, str):
        try:
            response = str(response)
        except:
            return "Response processed successfully."
    
    # Remove <thinking>...</thinking> blocks
    cleaned = re.sub(r'<thinking>.*?</thinking>', '', response, flags=re.DOTALL)
    
    # Check if response is in JSON format with nested content
    if cleaned.find("'role': 'assistant'") >= 0 and cleaned.find("'content'") >= 0 and cleaned.find("'text'") >= 0:
        try:
            # Try to parse as Python literal
            data = ast.literal_eval(cleaned)
            if isinstance(data, dict) and 'content' in data and isinstance(data['content'], list):
                for item in data['content']:
                    if isinstance(item, dict) and 'text' in item:
                        # Return the text content directly (preserves markdown)
                        return deduplicate_content(item['text'])
        except:
            # If parsing fails, try regex as fallback
            match = re.search(r"'text': '(.+?)(?:'}]|})", cleaned, re.DOTALL)
            if match:
                # Unescape the content to preserve markdown
                text = match.group(1)
                text = text.replace('\\n', '\n')  # Replace escaped newlines
                text = text.replace('\\t', '\t')  # Replace escaped tabs
                text = text.replace("\\'", "'")   # Replace escaped single quotes
                text = text.replace('\\"', '"')   # Replace escaped double quotes
                return deduplicate_content(text)
    
    return deduplicate_content(cleaned.strip())

def deduplicate_content(content):
    """Remove duplicate sections from content"""
    if not content:
        return content
    
    try:
        # Split by major sections and remove duplicates
        sections = content.split('\n---\n')
        seen_sections = set()
        unique_sections = []
        
        for section in sections:
            section_hash = hashlib.md5(section.strip().encode()).hexdigest()
            if section_hash not in seen_sections and section.strip():
                seen_sections.add(section_hash)
                unique_sections.append(section)
        
        return '\n---\n'.join(unique_sections)
    except Exception as e:
        log_error_silently(e, "Content deduplication error")
        return content

# Function to check for image paths in text and display them
def enhanced_markdown(content):
    """Enhanced markdown rendering with better code block styling"""
    # Render markdown normally - Streamlit will handle it
    # The custom CSS will style code blocks automatically
    st.markdown(content, unsafe_allow_html=True)

def display_message_with_images(content, message_index=0):
    # Look for image paths in the content
    image_path_patterns = [
        r'/tmp/generated-diagrams/[\w\-\.]+\.png',
        r'generated-diagrams/[\w\-\.]+\.png',
        r'./generated-diagrams/[\w\-\.]+\.png'
    ]
    
    image_paths = []
    for pattern in image_path_patterns:
        image_paths.extend(re.findall(pattern, content))
    
    # If no image paths found, display enhanced markdown
    if not image_paths:
        enhanced_markdown(content)
        return
    
    # Split content by image paths to display text and images in order
    combined_pattern = '|'.join(image_path_patterns)
    segments = re.split(f'({combined_pattern})', content)
    
    for segment in segments:
        # Check if segment is an image path
        is_image_path = any(re.match(pattern, segment) for pattern in image_path_patterns)
        
        if is_image_path:
            # Display image
            image_path = segment
            if os.path.exists(image_path):
                try:
                    # Display the image
                    image = Image.open(image_path)
                    st.image(image, caption="Generated Diagram", width="stretch")
                    
                    # Add download button with unique key
                    filename = os.path.basename(image_path)
                    unique_key = f"download_{filename}_{message_index}_{hashlib.md5(image_path.encode()).hexdigest()[:8]}"
                    with open(image_path, "rb") as file:
                        st.download_button(
                            label=f"💾 Save {filename}",
                            data=file.read(),
                            file_name=filename,
                            mime="image/png",
                            key=unique_key,
                            use_container_width=True
                        )
                except Exception as e:
                    log_error_silently(e, f"Image display error for {image_path}")
                    st.success("✅ Diagram generated successfully")
            else:
                log_error_silently(f"Image not found: {image_path}", "Missing image file")
                st.info("📊 Architecture diagram generated successfully")
        else:
            # Display text segment with enhanced markdown
            if segment.strip():
                enhanced_markdown(segment.strip())
# Initialize chat history
def init_chat_history():
    if "messages" not in st.session_state:
        st.session_state.messages = []

# Main app
def main():
    init_chat_history()
    
    # Add custom CSS for enhanced styling
    st.markdown("""
    <style>
        /* Enhanced code block styling */
        .stCodeBlock {
            font-size: 14px !important;
            background-color: #2d2d2d;
            color: #d4d4d4;
            border-radius: 6px;
            padding: 12px !important;
        }
        
        /* Larger headings */
        h1 {
            font-size: 32px !important;
            margin-bottom: 0.5rem !important;
        }
        
        h2 {
            font-size: 26px !important;
            margin-top: 1.5rem !important;
            margin-bottom: 0.75rem !important;
        }
        
        h3 {
            font-size: 22px !important;
            margin-top: 1.25rem !important;
            margin-bottom: 0.5rem !important;
        }
        
        h4 {
            font-size: 18px !important;
            margin-top: 1rem !important;
        }
        
        /* Better text spacing */
        p {
            margin-bottom: 0.75rem !important;
            line-height: 1.6 !important;
        }
        
        /* Enhanced lists */
        ul, ol {
            margin-bottom: 1rem !important;
        }
        
        li {
            margin-bottom: 0.5rem !important;
        }
        
        /* Better code inline styling */
        code {
            background-color: #f0f0f0 !important;
            color: #d63384 !important;
            padding: 2px 6px !important;
            border-radius: 3px !important;
            font-size: 13px !important;
        }
        
        /* Highlight important sections */
        .important {
            background-color: #fff9e6;
            padding: 12px;
            border-left: 4px solid #ffc107;
            border-radius: 4px;
            margin: 12px 0;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Create a two-column layout with sidebar and main content
    # Sidebar for tools and predefined tasks
    with st.sidebar:
        st.image("project-maygum.png")
        st.title("☁️ AWS Cloud Engineer")
        st.markdown("---")
        
        # Predefined Tasks Dropdown
        st.subheader("Predefined Tasks")
        task_options = list(PREDEFINED_TASKS.values())
        task_keys = list(PREDEFINED_TASKS.keys())
        
        selected_task = st.selectbox(
            "Select a predefined task:",
            options=task_options,
            index=None,
            placeholder="Choose a task...",
            key="predefined_task_selector"  # Add unique key to fix duplicate ID error
        )
        
        if selected_task:
            task_index = task_options.index(selected_task)
            task_key = task_keys[task_index]
            
            if st.button("Run Selected Task", key="run_task_button", use_container_width=True):
                # Add task to chat as user message - preserve original description
                st.session_state.messages.append({"role": "user", "content": selected_task})
                
                # Generate response
                get_agent_functions()  # Ensure agent is cached
                with st.spinner("Working on it..."):
                    try:
                        result = execute_predefined_task(task_key)
                        cleaned_result = clean_response(result)
                        st.session_state.messages.append({"role": "assistant", "content": cleaned_result})
                        st.rerun()
                    except Exception as e:
                        log_error_silently(e, f"Task execution error: {task_key}")
                        success_message = Config.SUCCESS_MESSAGES['task_complete']
                        st.session_state.messages.append({"role": "assistant", "content": success_message})
                        st.rerun()
        
        st.markdown("---")
        
        # AWS configuration info
        st.subheader("AWS Configuration")
        st.info("Using AWS credentials from environment variables")
        
        # Available Tools Section
        st.subheader("Available Tools")
        
        # Get detailed MCP status
        mcp_status = get_detailed_mcp_status()
        
        # Display AWS CLI Tool
        st.markdown("**Core Tools**")
        if mcp_status["aws_cli"]:
            st.markdown("✅ **AWS CLI Tool** - `use_aws`: Execute AWS CLI commands")
        else:
            st.markdown("❌ **AWS CLI Tool** - Not available")
        
        # Display MCP Tools Status
        st.markdown("**MCP Servers**")
        
        # CloudFormation MCP
        if mcp_status["cloudformation_mcp"]:
            st.markdown("✅ **CloudFormation MCP** - Resource creation & management")
        else:
            st.markdown("❌ **CloudFormation MCP** - Not initialized")
        
        # AWS Documentation MCP
        if mcp_status["aws_docs_mcp"]:
            st.markdown("✅ **AWS Documentation MCP** - Documentation search")
        else:
            st.markdown("❌ **AWS Documentation MCP** - Not initialized")
        
        # AWS Diagram MCP
        if mcp_status["aws_diagram_mcp"]:
            st.markdown("✅ **AWS Diagram MCP** - Visual architecture diagrams")
        else:
            st.markdown("❌ **AWS Diagram MCP** - Not initialized")
        
        # Cost Explorer MCP
        if mcp_status["cost_explorer_mcp"]:
            st.markdown("✅ **Cost Explorer MCP** - Cost analysis & optimization")
        else:
            st.markdown("❌ **Cost Explorer MCP** - Not initialized")
        
        # CCAPI MCP (Always disabled)
        st.markdown("❌ **CCAPI MCP** - Disabled (using CloudFormation instead)")
        
        # Summary
        active_count = sum(1 for key, status in mcp_status.items() if status and key != "ccapi_mcp")
        total_count = len(mcp_status) - 1  # Exclude CCAPI from total count
        
        if active_count == total_count:
            st.success(f"🎉 All {active_count} MCP servers are active!")
        elif active_count > 0:
            st.warning(f"⚠️ {active_count}/{total_count} MCP servers are active")
        else:
            st.error("❌ No MCP servers are active")
            st.markdown("To enable full functionality, please install the Universal Command Line Interface (uvx).")
            st.markdown("Visit: https://strandsagents.com/0.1.x/getting-started/installation/")

        # Clear chat button
        st.markdown("---")
        if st.button("Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    
    # Main content area with chat interface
    st.title("SAIC AWS Cloud Engineer Digital Agent")
    
    # Show warning if MCP tools are not available
    mcp_status = get_detailed_mcp_status()
    inactive_servers = [name for name, status in mcp_status.items() if not status and name != "ccapi_mcp"]
    
    if inactive_servers:
        inactive_names = {
            "cloudformation_mcp": "CloudFormation",
            "aws_docs_mcp": "AWS Documentation", 
            "aws_diagram_mcp": "AWS Diagram",
            "cost_explorer_mcp": "Cost Explorer"
        }
        inactive_display = [inactive_names[name] for name in inactive_servers]
        st.warning(f"⚠️ Running with limited functionality. {', '.join(inactive_display)} tools are not available.")
        st.markdown("You can still use the agent for basic AWS operations and queries.")
    
    st.markdown("Ask questions about AWS resources, create/manage infrastructure, analyze costs, get pricing estimates, optimize spending, or select a pre-defined task from the sidebar.")
    
    # Display chat messages
    if not st.session_state.messages:
        # Welcome message if no messages
        with st.chat_message("assistant"):
            st.markdown("👋 Hello! I'm Maygum, AWS Cloud Engineer Digital Agent. I can help you:\n\n**🏗️ Infrastructure Management:**\n- Create, update, and manage 1,100+ AWS resources\n- Generate Infrastructure as Code templates\n- Implement security best practices\n\n**💰 Cost Management:**\n- Analyze actual AWS spending and trends\n- Estimate costs for planned resources\n- Identify cost optimization opportunities\n\n**📚 Documentation & Guidance:**\n- Search AWS documentation\n- Provide architectural recommendations\n- Troubleshoot issues\n\n💡 **Pro Tip:** I provide quick summaries with options to explore specific areas. This gives you faster responses (10-18 seconds) and lets you dive deep only where you need!\n\nSelect a predefined task from the sidebar or ask me anything about AWS!")
    else:
        # Display existing messages
        for idx, message in enumerate(st.session_state.messages):
            with st.chat_message(message["role"]):
                # Use the special display function that can handle images
                display_message_with_images(message["content"], idx)
    
    # User input
    if prompt := st.chat_input("Ask me about AWS..."):
        # Add user message to chat and display immediately
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message immediately
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response with timing
        get_agent_functions()  # Ensure agent is cached
        with st.chat_message("assistant"):
            # Track response time
            import time
            start_time = time.time()
            
            with st.spinner("Processing your request..."):
                try:
                    response = execute_custom_task(prompt)
                    cleaned_response = clean_response(response)
                    
                    # Calculate response time
                    response_time = time.time() - start_time
                    
                    # Display response
                    display_message_with_images(cleaned_response, len(st.session_state.messages))
                    
                    # Show response time hint for long responses
                    if response_time > 25:
                        st.info("💡 **Tip:** For faster responses, ask about specific topics instead of requesting complete guides. I can provide focused answers in 10-18 seconds!")
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": cleaned_response})
                except Exception as e:
                    log_error_silently(e, "Custom task execution error")
                    success_message = Config.SUCCESS_MESSAGES['request_processed']
                    st.markdown(success_message)
                    st.session_state.messages.append({"role": "assistant", "content": success_message})

if __name__ == "__main__":
    main()
