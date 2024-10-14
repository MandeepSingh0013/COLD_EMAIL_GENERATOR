import chain_smith as cs

class FineTuner:
    def __init__(self, llm_model_name, api_key):
        self.rl_model = cs.RLHFModel(llm_model_name, api_key)

    def fine_tune_with_feedback(self, feedback_data):
        try:
            # Fine-tune LLM based on feedback data
            self.rl_model.fine_tune(feedback_data)
            st.success("Model successfully fine-tuned based on feedback.")
        except Exception as e:
            st.error(f"Error during fine-tuning: {e}")

# Fetch feedback data for fine-tuning
def collect_feedback_for_rlhf(collection):
    # Query ChromaDB to fetch all negative feedback for fine-tuning
    feedback_data = collection.get()  # Fetch all records
    negative_feedback = [item for item in feedback_data if item['feedback'] == "👎"]
    
    if negative_feedback:
        st.info("Starting fine-tuning process...")
        fine_tuner = FineTuner("LLama", "groq_api_key")
        fine_tuner.fine_tune_with_feedback(negative_feedback)
    else:
        st.info("No negative feedback available for fine-tuning.")
