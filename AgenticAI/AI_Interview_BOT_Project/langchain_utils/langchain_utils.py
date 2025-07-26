from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate  #  Added

#  Global cache to store MCQs
mcq_cache = []
asked_index = 0

# Load and prepare LangChain QA system
def setup_langchain_qa(doc_path):
    loader = TextLoader(doc_path)
    docs = loader.load()
    splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(docs)

    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(chunks, embeddings)
    retriever = vectorstore.as_retriever()

    #  Custom prompt to allow fallback if context is weak
    qa_prompt = PromptTemplate(
        input_variables=["context", "question"],
        template="""
Use the following context to answer the question. If the context is not relevant, answer using your own knowledge.

Context:
{context}

Question:
{question}
"""
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(model="gpt-4"),
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": qa_prompt}  # ✅ Injected custom prompt
    )
    return qa_chain

#  Extract key topics (MCQs) from the document using LLM
def suggest_topics(qa_chain):
    global mcq_cache
    prompt = "Extract all multiple-choice questions from the document. Format each as:\n\nQ: <question>\nA. <option>\nB. <option>\nC. <option>\nD. <option>\n"
    response = qa_chain.run(prompt)

    # Parse MCQs from response
    blocks = response.split("Q:")
    mcq_cache = [f"Q:{block.strip()}" for block in blocks if block.strip()]
    return [f"Question {i+1}" for i in range(len(mcq_cache))]

#  Generate a question from the cached MCQs
def generate_question(topic, qa_chain):
    global asked_index, mcq_cache
    if asked_index < len(mcq_cache):
        question = mcq_cache[asked_index]
        asked_index += 1
        return question
    else:
        return "No more questions available."

#  Evaluate an answer to a question
def evaluate_answer(question, answer, qa_chain):
    prompt = (
        f"Evaluate the following answer to the interview question.\n\n"
        f"Question: {question}\nAnswer: {answer}\n\n"
        f"Provide a score out of 10 and a brief explanation of the evaluation."
    )
    return qa_chain.run(prompt)

#  Generate a summary of the interview
def generate_summary(feedback_log, qa_chain):
    combined = "\n".join([
        f"Q: {entry['question']}\nA: {entry['answer']}\nEval: {entry['evaluation']}"
        for entry in feedback_log
    ])
    prompt = (
    "Based on the following interview transcript and evaluations, provide an overall summary of the candidate's performance.\n"
    "Do not provide individual scores for each question. Each correct answer earns 1 mark, with a maximum score of 5.\n"
    "At the end, provide a final score out of 5 and a brief overall feedback on the candidate's strengths and areas for improvement.\n\n"
    "use combined data only for understanding the candidate's performance:\n please do not its data in the summary.\n\n"
    f"{combined}"
)

    return qa_chain.run(prompt)