# import requests

# # Set your Hugging Face API token (replace 'your_token_here' with your actual API token)
# API_TOKEN = "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"

# # Headers for the API request
# headers = {
#     "Authorization": f"Bearer {API_TOKEN}"
# }

# def generate_test_questions(title):
#     try:
#         # Set the API endpoint for GPT-Neo (or any other Hugging Face model)
#         api_url = "https://api-inference.huggingface.co/models/EleutherAI/gpt-neo-2.7B"
        
#         # Construct the prompt
#         prompt = f"Generate five test questions for the topic: {title}. Each question should have three answers, with one correct answer marked as is_correct: true."
        
#         # Payload for the API request
#         payload = {
#             "inputs": prompt
#         }
        
#         # Make the request to the API
#         response = requests.post(api_url, headers=headers, json=payload)
        
#         # Check if the request was successful
#         if response.status_code == 200:
#             result = response.json()
#             # The result will contain the generated text
#             return result[0]['generated_text']
#         else:
#             return f"Error: {response.status_code}, {response.text}"

#     except Exception as e:
#         print(f"An error occurred: {e}")
#         return None

# # Example usage
# print(generate_test_questions("Ethical Hacking for Beginners"))
