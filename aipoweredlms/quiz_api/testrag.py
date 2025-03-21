from ragquiz import MCQGenerator

# Load existing vector database
mcq_gen = MCQGenerator()

# Generate MCQs
mcqs = mcq_gen.create_mcqs("machine learning medium", save_to_file=True)