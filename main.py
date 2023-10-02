import sqlite3
from tkinter import *
from tkinter import ttk

class AutocompleteCombobox(ttk.Combobox):
    def set_completion_list(self, completion_list):
        self._completion_list = sorted(completion_list, key=str.lower)
        self._hits = []
        self._hit_index = 0
        self.position = 0
        self.bind('<KeyRelease>', self.handle_keyrelease)

    def autocomplete(self, delta=0):
        if delta:
            self.delete(self.position, END)
        else:
            self.position = len(self.get())
        _hits = []
        for element in self._completion_list:
            if element.lower().startswith(self.get().lower()):
                _hits.append(element)
        if _hits != self._hits:
            self._hit_index = 0
            self._hits = _hits
        if _hits:
            self.delete(0, END)
            self.insert(0, self._hits[self._hit_index])
            self.select_range(self.position, END)

    def handle_keyrelease(self, event):
        if event.keysym == "BackSpace":
            self.delete(self.index(INSERT), END)
            self.position = self.index(END)
        if event.keysym == "Left":
            if self.position < self.index(END):
                self.delete(self.position, END)
        if event.keysym == "Right":
            self.position = self.index(END)
        if len(event.keysym) == 1:
            self.autocomplete()

# Diseases, descriptions, and symptoms
data = [
    ("Common Cold", "A viral infectious disease that primarily affects the respiratory tract, particularly the nose.", ["Runny or stuffy nose", "Sneezing", "Cough", "Sore throat", "Mild headache"]),
    ("Influenza (Flu)", "A viral infection that attacks your respiratory system - your nose, throat, and lungs.", ["Fever", "Cough", "Sore throat", "Runny or stuffy nose", "Body aches", "Headache", "Chills", "Fatigue"]),
    ("COVID-19", "An infectious disease caused by the SARS-CoV-2 coronavirus. Symptoms can range from mild to severe illness.", ["Fever", "Cough", "Shortness of breath", "Loss of taste or smell", "Fatigue", "Body aches"]),
    ("Hypertension (High Blood Pressure)", "A condition in which the long-term force of the blood against your artery walls is high enough to cause health problems, such as heart disease.", ["Headaches", "Shortness of breath", "Dizziness", "Chest pain", "Heart palpitations", "Nosebleeds"]),
    ("Diabetes", "A group of diseases that result in too much sugar in the blood (high blood glucose).", ["Increased thirst", "Frequent urination", "Hunger", "Fatigue", "Blurred vision"]),
    ("Asthma", "A condition in which a person's airways become inflamed, narrow, and swell, producing extra mucus, which makes it difficult to breathe.", ["Shortness of breath", "Chest tightness or pain", "Trouble sleeping due to shortness of breath", "Coughing or wheezing"]),
    ("Depression", "A mental health disorder characterized by a persistently depressed mood or loss of interest in activities, causing significant impairment in daily life.", ["Persistent sadness", "Loss of interest in activities", "Changes in sleep", "Difficulty concentrating", "Feelings of worthlessness"]),
    ("Anxiety Disorders", "A group of mental health disorders characterized by significant feelings of anxiety and fear.", ["Excessive worry", "Restlessness", "Trouble with concentration", "Sleep disturbances", "Fatigue"]),
    ("Heart Disease", "A broad term that generally refers to conditions that involve narrowed or blocked blood vessels that can lead to heart attack, chest pain (angina), or stroke.", ["Chest pain", "Shortness of breath", "Palpitations", "Fainting"]),
    ("Arthritis", "An inflammation of one or more of your joints that can cause pain and stiffness.", ["Joint pain", "Stiffness", "Swelling", "Decreased range of motion"]),
    ("Allergies", "Immune system reactions that occur in response to certain substances. Symptoms can range from mild to severe.", ["Sneezing", "Itching", "Rash", "Difficulty breathing"]),
    ("Gastroenteritis (Stomach Flu)", "An inflammation of the lining of the intestines caused by a virus, bacteria, or parasites.", ["Diarrhea", "Abdominal pain", "Vomiting", "Headache", "Fever", "Chills"]),
    ("Urinary Tract Infections (UTIs)", "An infection in any part of your urinary system, kidneys, bladder, or urethra.", ["Burning feeling during urination", "Frequent urination", "Cloudy or strong-smelling urine", "Lower abdominal pain"]),
    ("Osteoporosis", "A bone disease that occurs when the body loses too much bone, makes too little bone, or both.", ["Back pain", "Loss of height over time", "Stooped posture", "Bone fracture that occurs much more easily than expected"]),
    ("Dermatitis (Eczema)", "A group of diseases that result in inflammation of the skin.", ["Itchy", "Red", "Dry skin"]),
    ("Migraine", "A type of headache characterized by recurrent headaches that are moderate to severe.", ["Severe, throbbing headaches", "Nausea", "Vomiting", "Extreme sensitivity to light and sound"]),
    ("COPD (Chronic Obstructive Pulmonary Disease)", "A type of obstructive lung disease characterized by long-term breathing problems and poor airflow.", ["Shortness of breath", "Wheezing", "Chest tightness", "Chronic cough with mucus"]),
    ("Obesity", "A disorder involving excessive body fat that increases the risk of health problems.", ["Excessive body fat", "High body mass index (BMI)"]),
    ("Hyperlipidemia (High Cholesterol)", "Occurs when there are too many lipids or fats in the blood.", ["Routine blood tests are needed for diagnosis"]),
    ("GERD (Gastroesophageal Reflux Disease)", "A long-term condition where acid from the stomach comes up into the esophagus.", ["Heartburn", "Regurgitation of food or sour liquid", "Difficulty swallowing", "Sensation of a lump in the throat"])
]

def create_db():
    conn = sqlite3.connect('illnesses.db')
    c = conn.cursor()

    # Create table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS illnesses
                (name text, description text, symptom text)''')

    # Delete any existing data in the table
    c.execute("DELETE FROM illnesses")

    # Insert new data
    for name, description, symptoms in data:
        for symptom in symptoms:
            c.execute("INSERT INTO illnesses VALUES (?, ?, ?)", (name, description, symptom))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()


def search():
    search_term = search_entry.get().lower().strip()
    if search_term:
        conn = sqlite3.connect('illnesses.db')
        c = conn.cursor()

        c.execute("SELECT DISTINCT description FROM illnesses WHERE LOWER(name) LIKE ?", ('%' + search_term + '%',))
        description = c.fetchone()

        c.execute("SELECT symptom FROM illnesses WHERE LOWER(name) LIKE ?", ('%' + search_term + '%',))
        symptoms = c.fetchall()

        conn.close()

        illnesses_text = f'Illness: {search_term.capitalize()}\n'
        illnesses_text += f'Description: {description[0] if description else "No description available"}\n'
        illnesses_text += f'Symptoms: {", ".join(symptom[0] for symptom in symptoms)}\n'

        search_result.config(text=illnesses_text if illnesses_text else "No match found.")

def add_symptom():
    symptom = symptom_entry.get().strip()
    if symptom and symptom not in symptoms_list.get(0, END):
        symptoms_list.insert(END, symptom)

def remove_symptom():
    selected_symptoms = symptoms_list.curselection()
    symptoms_list.delete(selected_symptoms)

def clear_all():
    symptoms_list.delete(0, END)
    symptom_entry.delete(0, END)
    search_entry.delete(0, END)
    result.config(text='')
    search_result.config(text='')

def check_symptoms():
    conn = sqlite3.connect('illnesses.db')
    c = conn.cursor()

    illnesses_dict = {}  # Keep count of each illness
    descriptions_dict = {}  # Store descriptions for each illness
    for symptom in symptoms_list.get(0, END):
        symptom = symptom.lower().strip()  # Convert to lowercase and remove extra spaces
        c.execute("SELECT DISTINCT name, description FROM illnesses WHERE LOWER(symptom) = ?", (symptom,))  # Match in lowercase
        for illness, description in c.fetchall():
            if illness not in illnesses_dict:
                illnesses_dict[illness] = [symptom]
                descriptions_dict[illness] = description
            else:
                illnesses_dict[illness].append(symptom)

    conn.close()

    # Create a readable string of illnesses with at least 2 symptom matches
    illnesses_text = ''
    for illness, symptoms in illnesses_dict.items():
        if len(symptoms) >= 2:
            illnesses_text += f'Illness: {illness}\nDescription: {descriptions_dict[illness]}\nMatched Symptoms: {", ".join(symptoms)}\n\n'

    # Clear symptom list and symptom entry field after checking symptoms
    clear_all()

    # Display the result
    result.config(text=illnesses_text if illnesses_text else "No match found. Please try different symptoms.")

create_db()

root = Tk()
root.title('Medical Symptom Checker')

# Create the UI elements
symptom_label = Label(root, text='Enter a symptom:')
symptom_entry = AutocompleteCombobox(root)
add_button = Button(root, text='Add Symptom', command=add_symptom)
remove_button = Button(root, text='Remove Symptom', command=remove_symptom)
symptoms_list = Listbox(root)

check_button = Button(root, text='Check Symptoms', command=check_symptoms)
clear_button = Button(root, text='Clear All', command=clear_all)
result_label = Label(root, text='Possible Illnesses:')
result = Label(root, text='')

search_label = Label(root, text='Search an Illness:')
search_entry = AutocompleteCombobox(root)
search_button = Button(root, text='Search', command=search)
search_result_label = Label(root, text='Illness Details:')
search_result = Label(root, text='')

# Fetch all unique symptoms from the database to use as auto-complete entries
conn = sqlite3.connect('illnesses.db')
c = conn.cursor()

c.execute("SELECT DISTINCT symptom FROM illnesses")
symptoms = sorted(set([symptom[0] for symptom in c.fetchall()]))

c.execute("SELECT DISTINCT name FROM illnesses")
illnesses = sorted(set([illness[0] for illness in c.fetchall()]))


conn.close()

symptom_entry.set_completion_list(symptoms)
search_entry.set_completion_list(illnesses)

# Place the UI elements on the grid
symptom_label.grid(row=0, column=0)
symptom_entry.grid(row=0, column=1)
add_button.grid(row=1, column=0)
remove_button.grid(row=1, column=1)
symptoms_list.grid(row=2, column=0, columnspan=2)
check_button.grid(row=3, column=0)
clear_button.grid(row=3, column=1)
result_label.grid(row=4, column=0, columnspan=2)
result.grid(row=5, column=0, columnspan=2)

search_label.grid(row=6, column=0)
search_entry.grid(row=6, column=1)
search_button.grid(row=7, column=0, columnspan=2)
search_result_label.grid(row=8, column=0, columnspan=2)
search_result.grid(row=9, column=0, columnspan=2)

root.mainloop()