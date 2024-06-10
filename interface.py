import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import pandas as pd
import random
import Recommendation as rc

csv_file = r'C:\Users\user\Downloads\Büyük veri\movie_ratings_df.csv'
background_image_path = r'C:\Users\user\Downloads\Büyük Veri\arayüz_1.jpg'

def get_unique_films(csv_file):
    try:
        df = pd.read_csv(csv_file)
        unique_films = df['title'].dropna().unique().tolist()
        return unique_films, df
    except FileNotFoundError:
        print(f"File '{csv_file}' not found.")
        return [], None

def on_film_select(event):
    selected_film = combo_box_film_1.get()
    remaining_films = [film for film in film_list if film != selected_film]
    combo_box_film_2['values'] = remaining_films
    combo_box_film_2.set("Film seçiniz...")

def on_second_film_select(event):
    selected_film_2 = combo_box_film_2.get()

def rate_first_film():
    selected_rating = combo_box_rating_1.get()
    if selected_rating == "Puan seçiniz...":
        label_rating_1.config(text="Film için oy veriniz")

def rate_second_film():
    selected_rating = combo_box_rating_2.get()
    if selected_rating == "Puan seçiniz...":
        label_rating_2.config(text="Film için oy veriniz")

def filter_films(event):
    typed = combo_box_film_1.get()
    if typed == '':
        combo_box_film_1.set("")  # Clear the Combobox
        combo_box_film_1['values'] = film_list
    else:
        filtered_films = [film for film in film_list if film.lower().startswith(typed.lower())]
        combo_box_film_1['values'] = filtered_films

def filter_films_2(event):
    typed = combo_box_film_2.get()
    if typed == '':
        combo_box_film_2.set("")  # Clear the Combobox
        combo_box_film_2['values'] = film_list
    else:
        filtered_films = [film for film in film_list if film.lower().startswith(typed.lower())]
        combo_box_film_2['values'] = filtered_films

def find_matching_ids():
    global df, df_filtered_1, df_filtered_2, selected_film_1, selected_film_2, user_id

    selected_film_1 = combo_box_film_1.get()
    selected_film_2 = combo_box_film_2.get()
    selected_rating_1 = combo_box_rating_1.get()
    selected_rating_2 = combo_box_rating_2.get()

    user_id = None

    if selected_film_1 != "Film seçiniz..." and selected_rating_1 != "Puan seçiniz..." \
            and selected_film_2 != "Film seçiniz..." and selected_rating_2 != "Puan seçiniz...":

        # Filter users and ratings for the selected films
        df_filtered_1 = df[(df['title'] == selected_film_1) & (df['rating'] == int(selected_rating_1))]
        df_filtered_2 = df[(df['title'] == selected_film_2) & (df['rating'] == int(selected_rating_2))]

        if not df_filtered_1.empty and not df_filtered_2.empty:
            # Find common user IDs for both films
            id_1_list = df_filtered_1['userId'].tolist()
            id_2_list = df_filtered_2['userId'].tolist()
            common_ids = list(set(id_1_list).intersection(id_2_list))

            if common_ids:
                user_id = random.choice(common_ids)
                return user_id
            else:
                # Find user ID for each film if no common IDs
                user_id_1 = random.choice(id_1_list) if id_1_list else None
                user_id_2 = random.choice(id_2_list) if id_2_list else None

                if user_id_1:
                    user_id = user_id_1
                return user_id
            if user_id_2:
                user_id = user_id_2
                return user_id
            if not user_id_1 and not user_id_2:
                user_id = random.choice(df['userId'].tolist())
                return user_id
    else:
        result_label.config(text="Lütfen her iki filmi ve puanlarını seçiniz.")

def on_focus_in(event, placeholder_text):
    if event.widget.get() == placeholder_text:
        event.widget.set('')

def on_focus_out(event, placeholder_text):
    if event.widget.get() == '':
        event.widget.set(placeholder_text)

root = tk.Tk()
root.geometry("1000x700")
root.config(bg="white")
root.title("Film Öneri Sistemi")
root.resizable(False, False)

def resize_bg_image(event):
    new_width = event.width
    new_height = event.height
    resized_bg_image = bg_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    new_bg_photo = ImageTk.PhotoImage(resized_bg_image)
    canvas.create_image(0, 0, image=new_bg_photo, anchor="nw")
    canvas.image = new_bg_photo  # Save reference to avoid garbage collection

# Load the background image
bg_image = Image.open(background_image_path)
bg_photo = ImageTk.PhotoImage(bg_image)
bg_image.putalpha(int(255 * 0.75))
# Create a canvas widget and set the background image
canvas = tk.Canvas(root, width=bg_photo.width(), height=bg_photo.height())
canvas.pack(fill="both", expand=True)
canvas.create_image(0, 0, image=bg_photo, anchor="nw")
canvas.image = bg_photo  # Keep a reference to avoid garbage collection

# Create a main frame to hold all widgets
main_frame = tk.Frame(canvas, bg="#ffffff")
main_frame.place(relx=0.5, rely=0.5, anchor="center")
# Film selection frame
film_frame = tk.Frame(main_frame, bg="#ffffff")
film_frame.pack(fill="x", padx=10, pady=5)

label_film_1_prompt = tk.Label(film_frame, text="İzlediğiniz bir filmi seçiniz:", bg="#E0B0FF", fg="black")
label_film_1_prompt.pack(side="left", padx=5)

film_list, df = get_unique_films(csv_file)
film_list.sort()
combo_box_film_1 = ttk.Combobox(film_frame, values=film_list)
combo_box_film_1.pack(side="left", padx=5)
combo_box_film_1.set("Film seçiniz...")

combo_box_film_1.bind("<<ComboboxSelected>>", on_film_select)
combo_box_film_1.bind('<KeyRelease>', filter_films)
combo_box_film_1.bind('<FocusIn>', lambda event: on_focus_in(event, "Film seçiniz..."))
combo_box_film_1.bind('<FocusOut>', lambda event: on_focus_out(event, "Film seçiniz..."))

label_film_1 = tk.Label(main_frame, text="", bg="white", fg="black")
label_film_1.pack(pady=5)

# Rating selection frame
rating_frame = tk.Frame(main_frame, bg="#ffffff")
rating_frame.pack(fill="x", padx=10, pady=5)

label_rating_1_prompt = tk.Label(rating_frame, text="Puanınızı seçiniz (1-5) - Film 1: ", bg="#E0B0FF", fg="black")
label_rating_1_prompt.pack(side="left", padx=5)

ratings = ["1", "2", "3", "4", "5"]
combo_box_rating_1 = ttk.Combobox(rating_frame, values=ratings)
combo_box_rating_1.pack(side="left", padx=5)
combo_box_rating_1.set("Puan seçiniz...")

rate_button_1 = tk.Button(rating_frame, text="Oy Ver - Film 1", command=rate_first_film, bg="#E6E6FA", fg="black")
rate_button_1.pack(side="left", padx=5)

label_rating_1 = tk.Label(main_frame, text="", bg="white", fg="black")
label_rating_1.pack(pady=5)

# Second film selection frame
film_frame_2 = tk.Frame(main_frame, bg="#ffffff")
film_frame_2.pack(fill="x", padx=10, pady=5)

label_film_2_prompt = tk.Label(film_frame_2, text="İkinci bir filmi seçiniz: ", bg="#E0B0FF", fg="black")
label_film_2_prompt.pack(side="left", padx=5)

combo_box_film_2 = ttk.Combobox(film_frame_2, values=film_list)
combo_box_film_2.pack(side="left", padx=5)
combo_box_film_2.set("Film seçiniz...")

combo_box_film_2.bind("<<ComboboxSelected>>", on_second_film_select)
combo_box_film_2.bind('<KeyRelease>', filter_films_2)
combo_box_film_2.bind('<FocusIn>', lambda event: on_focus_in(event, "Film seçiniz..."))
combo_box_film_2.bind('<FocusOut>', lambda event: on_focus_out(event, "Film seçiniz..."))

label_film_2 = tk.Label(main_frame, text="", bg="white", fg="black")
label_film_2.pack(pady=5)

# Second rating selection frame
rating_frame_2 = tk.Frame(main_frame, bg="#ffffff")
rating_frame_2.pack(fill="x", padx=10, pady=5)

label_rating_2_prompt = tk.Label(rating_frame_2, text="Puanınızı seçiniz (1-5) - Film 2: ", bg="#E0B0FF", fg="black")
label_rating_2_prompt.pack(side="left", padx=5)

combo_box_rating_2 = ttk.Combobox(rating_frame_2, values=ratings)
combo_box_rating_2.pack(side="left", padx=5)
combo_box_rating_2.set("Puan seçiniz...")

rate_button_2 = tk.Button(rating_frame_2, text="Oy Ver - Film 2", command=rate_second_film, bg="#E6E6FA", fg="black")
rate_button_2.pack(side="left", padx=5)

label_rating_2 = tk.Label(main_frame, text="", bg="white", fg="black")
label_rating_2.pack(pady=5)

# Recommendations frame
recommendations_frame = tk.Frame(main_frame, bg="#ffffff")
recommendations_frame.pack(fill="x", padx=10, pady=5)

label_recommendations_prompt = tk.Label(recommendations_frame, text="Kaç adet film önerisi istersiniz?", bg="#E0B0FF", fg="black")
label_recommendations_prompt.pack(side="left", padx=5)

entry_num_recommendations = tk.Entry(recommendations_frame)
entry_num_recommendations.pack(side="left", padx=5)

def recommend_movies():
    num_recommendations = int(entry_num_recommendations.get())
    # Logic to generate movie recommendations goes here.
    # For now, let's just use some dummy data.
    #recommendations = [f"Film {i+1}" for i in range(num_recommendations)]
    recco = rc.top_movies(find_matching_ids(), num_recommendations)
    show_recommendations(recco)

def show_recommendations(reco):
    # This function will create a new window to display the movie recommendations.
    new_window = tk.Toplevel(root)
    new_window.title("Film Önerileri")
    new_window.geometry("1060x706")
    new_window.resizable(False, False)
    # Load the background image
    background_image = Image.open(r'C:\Users\user\Downloads\Büyük Veri\arayüz.jpg')
    background_photo = ImageTk.PhotoImage(background_image)

    # Create a canvas widget and set the background image
    canvas = tk.Canvas(new_window, width=background_photo.width(), height=background_photo.height())
    canvas.pack(fill="both", expand=True)
    canvas.create_image(0, 0, image=background_photo, anchor="nw")
    canvas.image = background_photo  # Save reference to avoid garbage collection
    # Create a main frame to hold all widgets
    main_frame = tk.Frame(canvas, bg="#ffffff")
    main_frame.place(relx=0.5, rely=0.5, anchor="center")
    
    # Function to handle resizing of the background image
    def resize_bg_image(event):
        new_width = event.width
        new_height = event.height
        resized_bg_image = background_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        new_bg_photo = ImageTk.PhotoImage(resized_bg_image)
        canvas.create_image(0, 0, image=new_bg_photo, anchor="nw")
        canvas.image = new_bg_photo  # Save reference to avoid garbage collection

    canvas.bind("<Configure>", resize_bg_image)

    # Create a frame to place widgets on top of the canvas
    frame = tk.Frame(canvas, bg="white")
    canvas.create_window((700,200 ), window=frame, anchor="nw")  # Changed to place the frame on the right side

    tk.Label(frame, text="Önerilen Filmler:", font=("Helvetica", 20), bg="white").pack(pady=10)
    
    tree = ttk.Treeview(frame)
    tree.pack(expand=True, fill='both')

    tree["columns"] = ["title"]
    tree["show"] = "headings"

    # Set up treeview columns
    tree.heading("title", text="Title")

    # Populate the treeview with movie recommendations
    pandas_df = reco.toPandas()
    for index, row in pandas_df.iterrows():
        tree.insert("", "end", values=(row["title"],))

# Example call to the function (make sure to define root and other necessary parts of your code)
# show_recommendations(recommendations)
btn_recommend = tk.Button(recommendations_frame, text="Film Öner", command=recommend_movies, bg="purple", fg="white", width=20, height=2, font=("Helvetica", 12, "bold"))
btn_recommend.pack(side="left", padx=5)

result_label = tk.Label(main_frame, text="", bg="#ffffff", fg="black", font=("Helvetica", 20, "italic"))
result_label.pack(pady=5)

root.mainloop()
