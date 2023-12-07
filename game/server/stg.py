from transformers import AutoProcessor, Blip2ForConditionalGeneration
import torch

class SketchToGuess:
    def __init__(self, modelName="Salesforce/blip2-opt-2.7b"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        assert self.device == "cuda", "CUDA Not Available."

        self.processor = AutoProcessor.from_pretrained(modelName)
        self.model = Blip2ForConditionalGeneration.from_pretrained(modelName, torch_dtype=torch.float16)
        self.model.to(self.device)
    
    # Takes in PIL Image
    def guess(self, image, miss=None):
        # if miss is None:
        #     prompt = "Question: In one word, what is this sketch of? Answer:"
        # else:
        #     prompt = "This sketch is NOT "+miss+". Question: What is this a sketch of? Answer:"
        #     print(prompt)
        prompt = "Question: In one word, what is this sketch of? Answer:"
        inputs = self.processor(image, text=prompt, return_tensors="pt").to(self.device, torch.float16)

        generated_ids = self.model.generate(**inputs, max_new_tokens=10)
        generated_text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()
        return generated_text