import googletrans


def read_srt(srt_path):

    with open(srt_path, 'r', encoding='utf-8') as file:
    
        lines = file.readlines()

    srt_subtitles = []

    start_time = None
    
    end_time = None
    
    text = []

    for line in lines:
        
        line = line.strip()
        
        if not line:
        
            if start_time is not None and end_time is not None:
        
                srt_subtitles.append([start_time, end_time, "\n".join(text[1:])])
        
                start_time = None
        
                end_time = None
        
                text = []
        
        elif '-->' in line:
        
            parts = line.split(' --> ')
        
            start_time = parts[0]
        
            end_time = parts[1]
        
        else:
        
            text.append(line)

    return srt_subtitles


def save_srt(srt_path, srt_subtitles):
    
    with open(srt_path, 'w', encoding='utf-8') as file:
    
        for i, sub in enumerate(srt_subtitles, start=1):
    
            file.write(f"{i}\n")
    
            file.write(f"{sub[0]} --> {sub[1]}\n")
    
            file.write(f"{sub[2]}\n")
    
            file.write("\n")

def get_languages():

    return googletrans.LANGUAGES


def translate_srt(srt_subtitles, src='en', dest='es'):

    translated_srt_subtitles = srt_subtitles

    translator = googletrans.Translator()

    i = 1
    
    for sub in translated_srt_subtitles:

        if sub[2]:
        
            sub[2] = translator.translate(text=sub[2], src=src, dest=dest).text

            print(f"(src: {src}, dest: {dest}) Translating subtitle... {i}/{len(translated_srt_subtitles)}", end="\r")

        i += 1

    return translated_srt_subtitles


def merge_srts(srt_subtitles_1, srt_subtitles_2):

    merged_srt_subtitles = srt_subtitles_1 + srt_subtitles_2

    merged_srt_subtitles.sort(key=lambda x: x[0])
    
    return merged_srt_subtitles