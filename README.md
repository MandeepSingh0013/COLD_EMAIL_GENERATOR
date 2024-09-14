# COLD_EMAIL_GENERATOR
USING GROQ API CREATING COLD EMAIL 
![image](https://github.com/user-attachments/assets/d0d9c18e-94b9-40aa-97f8-172d5b814e66)

![d6834be4-7863-4a94-ae2a-6a2372f37729](https://github.com/user-attachments/assets/b4821b0d-51da-41ad-b73a-0294b825badb)



📧 Cold Mail Generator
  
  This project is a Cold Mail Generator that leverages LLMs (Large Language Models) to extract job descriptions 
  from job postings and automatically generate personalized cold emails based on job requirements. 
  It helps business development executives to efficiently send targeted cold emails, 
  showcasing their company’s portfolio aligned with the required job skills.

🚀 Features
  Web Scraping Job Postings: Automatically scrapes job descriptions from URLs.
  Skill Matching: Extracts required skills from the job posting and matches them with the company portfolio.
  Portfolio Integration: Uses a portfolio of completed projects to suggest relevant links for the cold email.
  Cold Email Generation: Dynamically generates cold emails targeting specific job descriptions and skills.
  Support for Multiple LLMs: Choose between multiple LLMs such as LLama, Gemini, and GPT-4 to generate content.

🛠️ Technologies & Libraries
  Streamlit: For the user interface.
  Langchain: For working with large language models (LLMs).
  ChromaDB: For storing and querying portfolio information.
  Sentence Transformers: For embedding portfolio data.
  Pandas: For handling tabular data in the portfolio.
  Groq: For interacting with the LLM API and extracting job descriptions.
  Dotenv: For managing environment variables.

📂 Project Structure
  main.py: The entry point of the Streamlit application. It provides the interface for users to input job URLs, choose models, and generate emails.
  chains.py: Contains the logic to interact with the LLMs. It supports multiple models (LLama, Gemini, GPT-4) and handles job extraction and email writing.
  portfolio.py: Manages the portfolio using ChromaDB, loading the company’s past projects and matching them with the skills required for the job.
  utils.py: Utility functions, including cleaning scraped job text for easier processing.
  app/resource/my_portfolio.csv: A CSV file containing your portfolio data, including tech stacks and links to relevant projects.

🖥️ Getting Started
  Prerequisites
  Python 3.8+
  Streamlit
  Langchain
  ChromaDB
  Groq API Key



Usage
  Enter Job URL: Paste the URL of the job posting you want to target.
  Choose LLM: Select which large language model (LLama, Gemini, or GPT-4) to use for extracting job details and writing the email.
  Generate Email: The app will scrape the job description, extract relevant information, match it with your portfolio, and generate a cold email to be sent.
  Example
  Job Posting URL:
  Input: https://jobs.nike.com/job/R-31388?from=job%20search%20funnel
  
  Extracted Skills:
  Extracts key skills required for the job from the URL.
  
  Generated Cold Email:
  Based on the job description and your portfolio, the LLM will generate a targeted cold email, showcasing how your company can meet the requirements of the job.

Customization
  Portfolio: Update my_portfolio.csv with your company’s relevant tech stack and project links.
  LLM Models: You can easily add new LLMs or adjust the prompt templates in chains.py to improve email generation.
  🧪 Evaluation and Testing
  The project uses RAGAS metrics for evaluating the generated cold emails, ensuring that they are coherent, professional, and relevant to the extracted job descriptions.

To run evaluations, you can follow the steps below:

  Load the generated cold emails.
  Apply RAGAS metrics evaluation in the evaluation script.
  Future Enhancements
  Expand Portfolio Search: Improve the relevance of portfolio matches with advanced vector search techniques.
  Job Search Automation: Automatically scrape job listings from multiple websites.
  Advanced Email Personalization: Integrate advanced NLP to make emails more personalized based on individual job roles and industries.
🤝 Contributing
  We welcome contributions to enhance the functionality of this Cold Mail Generator. Feel free to open issues or submit pull requests.

📄 License
This project is licensed under the MIT License.

Reference: 
  https://www.youtube.com/watch?v=CO4E_9V6li0
  https://github.com/codebasics/project-genai-cold-email-generator.git
