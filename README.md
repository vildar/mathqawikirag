# MathWikiRag

This is a **Streamlit** app for evaluating how LLMs work for Mathematical Question Answering using RAG.

## Setup Instructions

1. **Install Ollama**

   Download and install Ollama from [https://ollama.com/download](https://ollama.com/download).  
   Make sure Ollama is installed and available in your terminal.

2. **Start Ollama Services**

   Open **two separate terminals**:

   - **Terminal 1:** Start the Ollama server

     ```
     ollama serve
     ```

   - **Terminal 2:** Run your model (replace `llama3.2:3b` with your model if different)
     ```
     ollama run llama3.2:3b
     ```

3. **Set Up Python Virtual Environment**

   In your project directory, run:

   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

   Replace venv with a name of your choice.

4. **Install Dependencies**

   ```
   pip install -r requirements.txt
   ```

5. **Configure Environment Variables**

   Create a `.env` file in your project directory with the following content:

   ```
   OLLAMA_URL=<YOUR-LOCAL-OLLAMA-SERVER-URL>
   LLM_NAME=llama3.2:3b
   ```

6. **Run the Streamlit App**

   ```
   streamlit run app.py
   ```

---

**Note:**

- Make sure the Ollama server and model are running before starting the Streamlit app.
- Adjust the model name in `.env` and `ollama run` if you use a different model.
