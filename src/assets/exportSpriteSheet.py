import json
import os
from tkinter import Tk, filedialog, Button, Frame, Radiobutton, IntVar
from PIL import Image

def save_spritesheet(frames, output_path, max_width):
    if not frames:
        return

    max_frame_width = max(frame.width for frame in frames)
    max_frame_height = max(frame.height for frame in frames)

    total_width = 0
    total_height = 0

    rows = []
    current_row = []
    current_row_height = 0
    current_row_width = 0

    for img in frames:
        if current_row_width + max_frame_width > max_width:
            rows.append((current_row, current_row_width, current_row_height))
            total_width = max(total_width, current_row_width)
            total_height += current_row_height
            current_row = []
            current_row_width = 0
            current_row_height = 0

        current_row.append(img)
        current_row_width += max_frame_width
        current_row_height = max(current_row_height, max_frame_height)

    rows.append((current_row, current_row_width, current_row_height))
    total_width = max(total_width, current_row_width)
    total_height += current_row_height

    spritesheet = Image.new('RGBA', (total_width, total_height))

    y_offset = 0
    for row, row_width, row_height in rows:
        x_offset = 0
        for img in row:
            frame_x = (max_frame_width - img.width) // 2
            frame_y = (max_frame_height - img.height) // 2
            spritesheet.paste(img, (x_offset + frame_x, y_offset + frame_y))
            x_offset += max_frame_width
        y_offset += max_frame_height

    try:
        spritesheet.save(output_path)
        print(f"Spritesheet salvo como {output_path}")
    except Exception as e:
        print(f"Erro ao salvar o spritesheet: {e}")

def save_frames_as_images(frames, output_dir, animation_name, variant, direction):
    if not frames:
        return

    anim_dir = os.path.join(output_dir, variant, animation_name, direction)
    os.makedirs(anim_dir, exist_ok=True)

    for i, img in enumerate(frames):
        frame_filename = os.path.join(anim_dir, f"frame_{i + 1}.png")
        try:
            img.save(frame_filename)
            print(f"Frame salvo como {frame_filename}")
        except Exception as e:
            print(f"Erro ao salvar o frame: {e}")

def process_files(json_file_paths, save_option):
    script_dir = os.path.dirname(os.path.abspath(__file__))

    for json_file_path in json_file_paths:
        try:
            base_name = os.path.splitext(os.path.basename(json_file_path))[0]
            output_dir = os.path.join(script_dir, base_name)
            os.makedirs(output_dir, exist_ok=True)

            with open(json_file_path, 'r') as json_file:
                data = json.load(json_file)

            textures = data.get('textures', [])
            if not textures:
                print(f"Nenhuma textura encontrada no JSON '{json_file_path}'.")
                continue

            texture = textures[0]
            spritesheet_filename = texture.get('image')
            if not spritesheet_filename:
                print(f"Nome do spritesheet não encontrado no JSON '{json_file_path}'.")
                continue

            spritesheet_path = os.path.join(os.path.dirname(json_file_path), spritesheet_filename)
            if not os.path.isfile(spritesheet_path):
                print(f"O arquivo de spritesheet '{spritesheet_filename}' não foi encontrado na pasta do JSON '{json_file_path}'.")
                continue

            spritesheet = Image.open(spritesheet_path)
            frames = texture.get('frames', [])

            animations = {}

            for sprite in frames:
                frame = sprite.get('frame')
                filename = sprite.get('filename')

                if not frame or not filename:
                    print(f"Dados ausentes para o sprite no JSON '{json_file_path}': {sprite}")
                    continue

                if 'Shadow' in filename:
                    continue

                parts = filename.split('/')
                if len(parts) < 4:
                    continue

                variant = parts[0]
                animation_name = parts[1]
                direction = parts[3]

                key = f"{variant}_{animation_name}_{direction}"
                if key not in animations:
                    animations[key] = []

                cropped_image = spritesheet.crop((
                    frame['x'],
                    frame['y'],
                    frame['x'] + frame['w'],
                    frame['y'] + frame['h']
                ))

                animations[key].append(cropped_image)

            for anim_key, frames in animations.items():
                frames = frames[::-1]  # Inverter a ordem das frames para salvar corretamente
                variant, animation_name, direction = anim_key.split('_')
                if save_option == 1:
                    output_filename = f"{anim_key}_spritesheet.png"
                    output_path = os.path.join(output_dir, output_filename)
                    save_spritesheet(frames, output_path, max_width=1024)
                elif save_option == 2:
                    save_frames_as_images(frames, output_dir, animation_name, variant, direction)

        except Exception as e:
            print(f"Erro ao processar o arquivo JSON '{json_file_path}': {e}")

def browse_json(save_option):
    file_paths = filedialog.askopenfilenames(filetypes=[("JSON files", "*.json")])
    if file_paths:
        process_files(file_paths, save_option)

root = Tk()
root.title("Processar Spritesheet")
root.geometry("400x300")

frame = Frame(root)
frame.pack(padx=10, pady=10, fill="both", expand=True)

save_option = IntVar()
save_option.set(1)

Radiobutton(frame, text="Criar Spritesheet para cada Animação", variable=save_option, value=1).pack(anchor="w")
Radiobutton(frame, text="Salvar cada Frame como Imagem Separada", variable=save_option, value=2).pack(anchor="w")

browse_json_button = Button(frame, text="Selecionar JSON", command=lambda: browse_json(save_option.get()))
browse_json_button.pack(pady=10)

root.mainloop()
