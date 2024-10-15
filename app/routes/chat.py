from flask import Blueprint, request, jsonify, make_response
from datetime import datetime
import uuid
import os
from dotenv import load_dotenv
load_dotenv(override=True)

from langchain.memory import ConversationBufferWindowMemory
from langchain_qdrant import QdrantVectorStore
from langchain.chains import ConversationalRetrievalChain

from extensions import db
from models import User, Rulebook, ChatHistory, ChatMessage
from chat_setup import llm, qdrant_url, embeddings

chat_blueprint = Blueprint('chat_blueprint', __name__)

@chat_blueprint.route('/send_message', methods =['POST'])
def send_message():
    # get json variables
    data = request.json
    message = data.get('message')
    user_id = data.get('user_id')
    chat_id = data.get('chat_id')
    game = data.get('game')

    new_history = False

    # find existing rulebook
    rulebook = Rulebook.query\
        .filter_by(id = game)\
        .first()

    if not rulebook:
        return jsonify({
                'message' : 'game not found'
            }), 404

    # setup llm
    memory = ConversationBufferWindowMemory(
        memory_key="chat_history",
        return_messages=True,
        k=3
    )
    # qdrant
    qdrant = QdrantVectorStore.from_existing_collection(
        embedding=embeddings,
        collection_name=rulebook.qdrant,
        url=qdrant_url,
        api_key=os.environ["QDRANT_KEY"],
    )
    retriever=qdrant.as_retriever()
    qa = ConversationalRetrievalChain.from_llm(
        llm,
        retriever=retriever,
        memory=memory
    )

    # find existing user
    user = User.query\
        .filter_by(public_id = user_id)\
        .first()
    # try to find existing chat history
    history = ChatHistory.query\
        .filter_by(public_id = chat_id)\
        .filter_by(game = game)\
        .first()

    if user:
        # if chat history does not exist, create it
        if not history:
            history = ChatHistory(
                public_id = str(uuid.uuid4()),
                # name = datetime.now().strftime("%a, %d %b %Y"),
                name = message,
                game = rulebook.id
            )
            user.chats.append(history)
            db.session.add(history)
            db.session.commit()
            new_history = True
        elif history:
            history_list = get_history(chat_id)['chats']
            input_message = ''
            output_message = ''
            for c in history_list:
                if len(input_message) == 0:
                    if c['is_human']:
                        input_message = c['message']
                        # print(input_message)
                if len(output_message) == 0:
                    if not c['is_human']:
                        output_message = c['message']
                        # print(output_message)
                if len(input_message) != 0 and len(output_message) != 0:
                    memory.save_context({'input': input_message}, {'output': output_message})
                    input_message = ''
                    output_message = ''

            # print(memory.load_memory_variables({}))
        # save user message to database
        new_user_chat = ChatMessage(
            public_id = str(uuid.uuid4()),
            is_human = True,
            date = datetime.now(),
            message = message
        )
        history.chats.append(new_user_chat)

        # invoke llm
        result = qa.invoke(message)
        # save ai message to database
        new_ai_chat = ChatMessage(
            public_id = str(uuid.uuid4()),
            is_human = False,
            date = datetime.now(),
            message = result['answer']
        )
        history.chats.append(new_ai_chat)

        # commit to database
        db.session.add_all([new_user_chat, new_ai_chat])
        db.session.commit()

        response = {
            "date": new_ai_chat.date.strftime("%a, %d %b %Y %X"),
            "is_human": False,
            "message": result['answer'],
            "is_new": new_history,
            "history_id": history.public_id
        }
    return jsonify(response)

@chat_blueprint.route('/get_history/<chat_id>', methods =['GET'])
def get_history(chat_id="-1"):

    # try to find existing chat history
    history = ChatHistory.query\
        .filter_by(public_id = chat_id)\
        .first()
    
    result = []
    if history:
        chats = ChatMessage.query\
            .filter_by(chat_id = chat_id)\
            .all()
        for c in chats:
            result.append({
                "date": c.date.strftime("%a, %d %b %Y %X"),
                "is_human": c.is_human,
                "message": c.message
            })
        rulebook = Rulebook.query\
            .filter_by(id = history.game)\
            .first()
    else:
        return jsonify({
                'message' : 'history not found'
            }), 404
    
    response = {
        "info": {
            "game": {
                "id": rulebook.id,
                "name": rulebook.name,
                "image": rulebook.image,
                "link": rulebook.link
            },
            "name": history.name,
            "public_id": history.public_id
        },
        "chats": result
    }
    
    return response

@chat_blueprint.route('/get_all_history/<user_id>', methods =['GET'])
def get_all_history(user_id="-1"):

    # try to find existing chat history
    user = User.query\
        .filter_by(public_id = user_id)\
        .first()
    
    result = []
    if user:
        history = ChatHistory.query\
            .filter_by(user_id = user_id)\
            .all()
        for h in history:
            result.append({
                "name": h.name,
                "game": h.game,
                "public_id": h.public_id
            })
    else:
        return jsonify({
                'message' : 'user not found'
            }), 404
    
    return result

@chat_blueprint.route('/delete_history', methods =['POST'])
def delete_history():
    # creates dictionary of form data
    data = request.json
    public_id = data.get('public_id')

    history = ChatHistory.query\
        .filter_by(public_id = public_id)\
        .first()
    
    if not history:
        # returns 401 if user does not exist
        return make_response(
            'Could not verify',
            401,
            {'WWW-Authenticate' : 'Basic realm ="Chat History does not exist !!"'}
        )

    db.session.delete(history)
    db.session.commit()
    return make_response('delete history')