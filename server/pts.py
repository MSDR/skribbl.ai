from diffusers import UNet2DConditionModel, LMSDiscreteScheduler, StableDiffusionPipeline
from diffusers.pipelines.stable_diffusion import StableDiffusionSafetyChecker
from transformers import CLIPTextModel, CLIPTokenizer, CLIPImageProcessor, CLIPVisionModel
import torch

class PromptToSketch:
    def __init__(self, checkpoint="./checkpoint"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        assert self.device == "cuda", "CUDA Not Available."
        self.pipe = StableDiffusionPipeline.from_pretrained(checkpoint, local_files_only=True).to(self.device)

    def sketch(self, prompt):
        return self.pipe(prompt).images[0]