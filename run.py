import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
import webbrowser
import numpy as np

from mrz import Loader, get_content, parse_mrz
from mrz import init_db, get_all_documents, save_document_to_db, delete_document_from_db


class OCRApp:
    def __init__(self, root):
        self.root = root

        self.root.title("OCR Document Reader")
        self.root.geometry("900x500")
        self.root.resizable(False, False)
        self.root.configure(bg="#f2f2f2")
        

        self.main_frame = tk.Frame(self.root, bg="#f2f2f2")
        self.main_frame.pack(fill="both", expand=True)

        self.left_frame = tk.Frame(self.main_frame, width=260, bg="#ffffff", bd=2, relief="groove")
        self.left_frame.pack(side="left", fill="y", padx=10, pady=10)

        self.upload_label = tk.Label(self.left_frame, text="Téléversez un document", font=("Arial", 11, "bold"), bg="white")
        self.upload_label.pack(pady=(10, 5))

        self.upload_icon = ImageTk.PhotoImage(Image.open("upload.png").resize((64, 64)))
        self.drop_area = tk.Label(self.left_frame, image=self.upload_icon, bg="#e6f7ff", width=80, height=80, relief="ridge")
        self.drop_area.pack(pady=(5, 10))

        self.btn_upload = ttk.Button(self.left_frame, text="📁 Choisir un fichier", command=self.load_document)
        self.btn_upload.pack(pady=(5, 15), ipadx=10)

        self.btn_history = ttk.Button(self.left_frame, text="🕘 Historique", command=self.show_history)
        self.btn_history.pack(pady=5, ipadx=10)

        self.btn_home = ttk.Button(self.left_frame, text="🏠 Accueil", command=self.show_home)
        self.btn_home.pack(pady=5, ipadx=10)

        self.right_frame = tk.Frame(self.main_frame, bg="#f2f2f2")
        self.right_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.result_canvas = tk.Canvas(self.right_frame, bg="#f8f8f8")
        self.scrollbar = tk.Scrollbar(self.right_frame, orient="vertical", command=self.result_canvas.yview)
        self.scrollable_result = tk.Frame(self.result_canvas, bg="#f8f8f8")

        self.scrollable_result.bind("<Configure>", lambda e: self.result_canvas.configure(scrollregion=self.result_canvas.bbox("all")))
        self.result_canvas.create_window((0, 0), window=self.scrollable_result, anchor="nw")
        self.result_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.result_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.show_home()


    def clear_results(self):
        for widget in self.scrollable_result.winfo_children():
            widget.destroy()


    def show_home(self):
        self.clear_results()

        home_frame = tk.Frame(self.scrollable_result, bg="white")
        home_frame.pack(fill="both", expand=True)

        centered_frame = tk.Frame(home_frame, bg="white")
        centered_frame.pack(pady=80)

        title = tk.Label(centered_frame, text="Bienvenue dans l'application OCR",
                     font=("Helvetica", 16, "bold"), bg="white", fg="#333")
        title.pack(pady=(0, 15))

        description = tk.Label(centered_frame,
        text="Cette application utilise la technologie OCR avec détection MRZ\n"
         "pour extraire automatiquement les informations des CIN et passeports.\n"
         "Développée par Youssef Bachar.",
        font=("Arial", 12), bg="white", fg="#555", justify="center"
)
        description.pack(pady=(0, 20))


        try:
            github_image = Image.open("github.png")
            github_image = github_image.resize((40, 40), Image.Resampling.LANCZOS)
            github_photo = ImageTk.PhotoImage(github_image)

            github_label = tk.Label(centered_frame, image=github_photo, bg="white", cursor="hand2")
            github_label.image = github_photo
            github_label.pack(pady=(10, 5))

            github_label.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/Youssef8400"))

            github_text = tk.Label(centered_frame, text="Voir sur GitHub", font=("Arial", 10, "underline"), fg="blue", bg="white", cursor="hand2")
            github_text.pack()
            github_text.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/Youssef8400"))

        except Exception as e:
            print(f"Erreur chargement icône GitHub : {e}")


    def show_history(self):
        self.clear_results()
        records = get_all_documents()
        for record in records:
            doc_id, doc_type, country, fname, lname, dnumber, sex, bdate, edate, img_path = record
            frame = tk.Frame(self.scrollable_result, borderwidth=1, relief="groove", bg="white", padx=10, pady=5)
            frame.pack(fill="x", padx=10, pady=5)
            try:
                img = Image.open(img_path)
                img.thumbnail((100, 100))
                img_tk = ImageTk.PhotoImage(img)
                img_label = tk.Label(frame, image=img_tk, cursor="hand2")
                img_label.image = img_tk
                img_label.pack(side="left", padx=10)
                img_label.bind(
                    "<Button-1>",
                    lambda e, r=record: self.display_result(
                        {
                            "Document Type": r[1],
                            "Country Code": r[2],
                            "First Name": r[3],
                            "Last Name": r[4],
                            "Document Number": r[5],
                            "Sex": r[6],
                            "Birth Date": r[7],
                            "Expire Date": r[8]
                        },
                        r[9]
                    )
                )
            except Exception:
                pass

            info = tk.Label(
                frame,
                text=f"Type: {doc_type}\nNom: {fname} {lname}\nNuméro: {dnumber}\nSexe: {sex}\nNaissance: {bdate}\nExpiration: {edate}",
                justify="left", bg="white", font=("Arial", 10)
            )
            info.pack(side="left", padx=10)

            btn_del = ttk.Button(
                frame,
                text="Supprimer",
                command=lambda id=doc_id: self._confirm_delete(id)
            )
            btn_del.pack(side="right", padx=10)


    def display_result(self, data, image_path=None):
        self.clear_results()

        outer_frame = tk.Frame(self.scrollable_result, bg="#ffffff", bd=2, relief="ridge", padx=20, pady=20)
        outer_frame.pack(pady=20, padx=30, fill="both", expand=True)

        img_and_info_frame = tk.Frame(outer_frame, bg="#ffffff")
        img_and_info_frame.pack(pady=10, padx=10)

        if image_path and os.path.exists(image_path):
            try:
                img = Image.open(image_path)
                img.thumbnail((300, 300))
                img_tk = ImageTk.PhotoImage(img)

                img_label = tk.Label(img_and_info_frame, image=img_tk, bg="white", bd=2, relief="solid")
                img_label.image = img_tk
                img_label.pack(pady=(0, 15))
            except Exception as e:
                print(f"Erreur chargement image : {e}")

        result_frame = tk.Frame(img_and_info_frame, bg="#f9f9f9", bd=1, relief="solid", padx=15, pady=10)
        result_frame.pack(pady=10, fill="both", expand=True)

        for key, value in data.items():
            lbl = tk.Label(result_frame, text=f"{key}: {value}", anchor="w", bg="#f9f9f9", font=("Arial", 10))
            lbl.pack(anchor="w", pady=2)


    def _confirm_delete(self, document_id):
        if messagebox.askyesno("Supprimer", "Voulez-vous vraiment supprimer cet élément de l'historique ?"):
            delete_document_from_db(document_id)
            self.show_history()


    def load_document(self):
        filepath = filedialog.askopenfilename(filetypes=[("Images or PDFs", "*.jpg *.jpeg *.png *.pdf")])
        if not filepath:
            return
        try:
            loader = Loader(file=filepath)
            img = loader()
            if img is None:
                messagebox.showerror("Erreur", "Impossible de charger le fichier.")
                return

            img_pil = Image.fromarray((img * 255).astype(np.uint8)) if img.max() <= 1.0 else Image.fromarray(img)
            temp_path = "temp_img.jpg"
            img_pil.convert("RGB").save(temp_path)
            text = get_content(temp_path)
            os.remove(temp_path)

            mrz_lines = [line.strip() for line in text.split('\n') if line.count('<') > 5]
            if not mrz_lines:
                raise ValueError(f"Aucune ligne MRZ détectée.\nOCR brut:\n{text}")

            document = parse_mrz('\n'.join(mrz_lines))
            data = document.to_dict()

            self.display_result(data, filepath)
            save_document_to_db(data, filepath)

        except Exception as e:
            self.clear_results()
            lbl = tk.Label(self.scrollable_result, text=f"Erreur : {str(e)}", bg="white", fg="red", font=("Arial", 10))
            lbl.pack(pady=10, padx=10)


if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    root.iconbitmap("favicon.ico")
    app = OCRApp(root)
    root.mainloop()
