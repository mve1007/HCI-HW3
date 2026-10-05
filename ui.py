# Quick note I used a lot of notes online about the tailwind and quasar for CSS for the styling (nothing copied but just overall help)
# https://quasar.dev
# https://tailwindcss.com
# https://paletacolorpro.com/en/tailwind-color-guide
# https://nicegui.io

# There were other reasource I wanted to reference but I can't find the old tabs


from nicegui import ui
import requests

API_URL = "http://localhost:8005"

questions = []
page_body = ui.column()

def api_get(path):
    try:
        # Attempt to send GET request to API
        response = requests.get(f"{API_URL}{path}", timeout=5)
        # If we get an error code back, raise an exception
        response.raise_for_status()
        # Otherwise, GET was successful so return response data
        return response.json()
    except requests.RequestException as e:
        # GET request was unsuccessful
        # Send an alert with error details to the UI and return empty list
        ui.notify(f"Could not reach API: {e}", type="negative")
        return []

def api_post(path, data):
    try:
        # Attempt to send POST request to API with data payload
        response = requests.post(f"{API_URL}{path}", json=data, timeout=5)
        # If we get an error code back, raise an exception
        response.raise_for_status()
        # Otherwise, POST was successful so return True
        return True
    except requests.RequestException as e:
        # POST request was unsuccessful
        # Send an alert with error details to the UI and return False
        ui.notify(f"Could not reach API: {e}", type="negative")
        return False

# TODO: Create api_delete function that attempts to send a DELETE request to the API.
# The request method should use the string f"{API_URL}{path}/{id}" to access the correct path,
# where id refers to the id number of the question to be deleted. 
def api_delete(path, id):
    try:
        response = requests.delete(f"{API_URL}{path}/{id}", timeout=5)
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        ui.notify(f"Could not reach API: {e}", type="negative")
        return False

# TODO: Create api_put function that attempts to send a PUT request to the API.
# The request method should use the string f"{API_URL}{path}/{id}" to access the correct path,
# where id refers to the id number of the question to be deleted. The data passed as an argument
# to this function must be sent with the request so that the API knows the updated values to add 
# to the dataset (similar to how data is sent in api_post).
def api_put(path, id, data):
    try:
        response = requests.put(f"{API_URL}{path}/{id}", json=data, timeout=5)
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        ui.notify(f"Could not reach API: {e}", type="negative")
        return False


# This function just helps with the deletion of a question while also refreshing the page when done
def delete_and_refresh(question_id):
    if api_delete("/delete", question_id):
        # This si to just help show the user that the request went through
        ui.notify("Question deleted successfully", type="positive") 
        render_page()


# This whole function helps create and manage the edit dialog for a question 
def open_edit_dialog(question):
    with ui.dialog() as dialog, ui.card().classes("w-96 p-6 shadow-xl rounded-lg"):
        ui.label("Edit Question").classes("text-xl font-bold text-gray-800")
        
        ui.label("Question:").classes("text-sm text-gray-600 font-semibold mt-2")
        new_q = ui.textarea(value=question["q"]).classes("w-full").props("outlined rows=3")
        
        ui.label("Answer:").classes("text-sm text-gray-600 font-semibold mt-2")
        new_a = ui.textarea(value=question["a"]).classes("w-full").props("outlined rows=2")
        
        with ui.row().classes("w-full justify-end gap-2 mt-4"):
            ui.button("Cancel", on_click=dialog.close).props("flat color=grey")
            ui.button(
                "Update question",
                on_click=lambda: [
                    dialog.close(),
                    api_put("/update", question["id"], {
                        "question": new_q.value,
                        "answer": new_a.value
                    }),
                    render_page()
                ]
            ).props("color=primary")
            
    dialog.open()

# TODO: Add edit and delete buttons dynamically to each question card. 
def render_question(question):
    with ui.card().classes("w-full shadow-md hover:shadow-lg transition-shadow duration-200 cursor-pointer p-4 rounded-xl border border-gray-100") as card:
        card.on("click", lambda: toggle_answer(question["id"]))
        
        with ui.row().classes("w-full justify-between items-start"):
            with ui.column().classes("flex-grow pr-4"):
                ui.label(question["q"]).classes("text-base font-medium text-gray-900")
                ui.label(f"Answer: {question['a']}").classes(
                    "text-sm text-emerald-700 font-semibold mt-2 bg-emerald-50 p-2 rounded border border-emerald-200"
                ).bind_visibility_from(question["state"], "show_answer")
            
            # Note: The .stop() prevents triggering the card's click event
            # Note: The .stop modifier prevents triggering the card's click event
            with ui.row().classes("gap-1 items-center"):
                ui.button(icon="edit").on("click.stop", lambda: open_edit_dialog(question)).props("flat round dense color=primary")
                ui.button(icon="delete").on("click.stop", lambda: delete_and_refresh(question["id"])).props("flat round dense color=negative")

def toggle_answer(q_id):
    for item in questions:
        if item["id"] == q_id:
            item["state"]["show_answer"] = not item["state"]["show_answer"]
            break

def add_new_question(question, answer):
    if not question.strip() or not answer.strip():
        ui.notify("Both question and answer are required.", type="warning")
        return
    api_post("/add", {"question": question, "answer": answer})
    render_page()

def render_text_inputs():
    with ui.card().classes("w-full p-5 mt-6 border border-blue-100 bg-blue-50/30 rounded-xl"):
        ui.label("Add a New Question").classes("text-lg font-bold text-gray-800 mb-2")
        new_question_input = ui.input(label="Question").props("outlined clearable").classes("w-full mb-2")
        new_answer_input = ui.input(label="Answer").props("outlined clearable").classes("w-full mb-3")
        ui.button(
            text="Add question",
            icon="add",
            on_click=lambda: add_new_question(
                question=new_question_input.value or "",
                answer=new_answer_input.value or ""
            )
        ).props("color=primary unelevated")

def init_page():
    render_page()

def render_page():
    global questions
    questions = api_get("/questions")
    page_body.clear()
    with page_body:
        ui.label("Flashcard Review App").classes("text-3xl font-extrabold text-gray-800 text-center w-full my-2")
        ui.label("Click any question card to reveal or hide the answer.").classes("text-sm text-gray-500 text-center w-full mb-2")
        
        for question in questions:
            question["state"] = {"show_answer": False}
            render_question(question)
            
        render_text_inputs()
    

init_page()
ui.run(port=8084, title="HCI Review Application")