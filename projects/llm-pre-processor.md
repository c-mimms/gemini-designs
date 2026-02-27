# LLM Pre-Processor Design

## System Overview

A lightweight, fast, and cost-effective language model (LLM) that acts as an intelligent "pre-processor" for all incoming requests. Its primary function is to analyze the user's intent and dynamically construct a highly optimized prompt for a more powerful, primary LLM. This pre-processor will select personas, gather necessary context, and format the final prompt to ensure the most accurate and efficient response.

## Dynamic Prompt Construction

The pre-processor will output a JSON object that dictates how the primary LLM should behave.

### 1. Persona Selection

The pre-processor will analyze the request to determine the most appropriate persona for the primary LLM to adopt.

- **Creative/Generative Tasks:** For requests involving writing, brainstorming, or creative content generation, it will select a persona like `CREATIVE_WRITER`.
- **Technical/Coding Tasks:** For requests involving code generation, debugging, or technical explanations, it will select a persona like `SENIOR_ENGINEER`.
- **General Queries:** For simple questions or tasks, a `DEFAULT_ASSISTANT` persona will be used.

### 2. Context Inclusion

The pre-processor will determine what contextual information is necessary for the primary LLM to fulfill the request accurately.

- **Message History:** Include recent and relevant conversation history.
- **File Context:** If the user references a file, the pre-processor will identify the file path and instruct the primary LLM to read its content.
- **Web Search:** If the request requires real-time information, it will trigger a web search and include the results in the context.

## Model Selection

The pre-processor should be a small, fast, and inexpensive model. Good candidates include:

- **Gemini 1.5 Flash**
- **Llama 3 8B**
- **Phi-3 Mini**

The goal is to minimize latency and cost at the pre-processing stage.

## Workflow

1.  **Request Ingestion:** The system receives the initial user request.
2.  **Pre-processing:** The request is sent to the pre-processor LLM.
3.  **Analysis & Structuring:** The pre-processor analyzes the intent, determines the required persona and context, and generates a JSON output.
    ```json
    {
      "persona": "SENIOR_ENGINEER",
      "context": [
        "MESSAGE_HISTORY",
        "FILE:src/app/main.py"
      ],
      "prompt": "The user wants to add a '/status' endpoint to the FastAPI app. Here is the relevant file content..."
    }
    ```
4.  **Primary Processing:** The JSON object is used to build the final prompt for the primary, more powerful LLM.
5.  **Response Generation:** The primary LLM generates the response based on the structured prompt.

## Use Cases & Benefits

- **Increased Accuracy:** By providing tailored context and personas, responses from the primary LLM will be more relevant and accurate.
- **Cost Efficiency:** Offloading the analysis task to a smaller, cheaper model reduces the token count and computational load on the more expensive primary model.
- **Personalized Interaction:** Dynamically changing personas creates a more engaging and personalized user experience.
- **Reduced Latency:** The smaller model can quickly analyze the request and prepare the prompt, potentially reducing overall response time.
