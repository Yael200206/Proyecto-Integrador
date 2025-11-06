import google.generativeai as genai

genai.configure(api_key="AIzaSyDrX6RpIQK4NVGu4YYoRChex_Vp3KYMuBE")

for m in genai.list_models():
    print(m.name)
