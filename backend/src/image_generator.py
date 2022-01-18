import torch
import numpy as np
from pathlib import Path
from PIL import Image

from src.context import (
    PATH_TO_GANSPACE,
    Config,
    get_instrumented_model,
    get_or_compute)

PATH_PRETRAINED_STYLEGAN = f'{PATH_TO_GANSPACE}/cache/components/stylegan2-ffhq_style_ipca_c80_n1000_w.npz'

class PCAStyleGan(torch.nn.Module):

    def __init__(self):
        super(PCAStyleGan, self).__init__() 
        # Speed up computation
        torch.autograd.set_grad_enabled(False)
        torch.backends.cudnn.benchmark = False

        # Specify model to use
        config = Config(
            model='StyleGAN2',
            layer='style',
            output_class='ffhq',
            components=80,
            use_w=True,
            n=1_000,
            batch_size=200
        )

        inst = get_instrumented_model(
            config.model,
            config.output_class,
            config.layer,
            torch.device('cuda'),
            use_w=config.use_w
        )

        get_or_compute(config, inst)
        self.model = inst.model.model

        with np.load(Path(__file__).parent / PATH_PRETRAINED_STYLEGAN) as data:
            self.lat_mean = torch.from_numpy(data['lat_mean']).cuda().float()

        self.edits_tensor = PCAStyleGANEdits()

    def forward(self, edits, seed=0):
        edits = self.edits_tensor(edits)
        edits = edits.cuda()

        torch.manual_seed(seed)
        random_sample = torch.randn(size=(1, 512), dtype=torch.float32, device='cuda')

        w = self.model.get_latent(random_sample).repeat_interleave(18, dim=0).unsqueeze(dim=1)

        w_new = w + edits
        img, _ = self.model(
            w_new,
            noise=self.model.make_noise(),
            truncation=0.7,
            truncation_latent=self.lat_mean
        )

        return img

    def generate_image(self, edits, size, seed=0): 
        img = self.forward(edits, seed)

        img_np = 0.5*(img+1)
        img_np = img_np.permute(0, 2, 3, 1).cpu().detach().numpy()
        img_np = np.clip(img_np, 0.0, 1.0).squeeze()
        img_np = Image.fromarray((img_np*255).astype(np.uint8), 'RGB')
        img_np = img_np.resize((size, size), resample=Image.BILINEAR)

        return img_np

class PCAStyleGANEdits(torch.nn.Module):
    def __init__(self):
        super(PCAStyleGANEdits, self).__init__()

        with np.load(Path(__file__).parent / PATH_PRETRAINED_STYLEGAN) as data:
            self.lat_comp = torch.from_numpy(data['lat_comp'])

    def forward(self, edits):
        out = torch.zeros((18, 1, 512), requires_grad=False, dtype=torch.float32)

        for entry in edits:
            edit_id = int(entry['id'])
            edit_value = float(entry['value'])

            out = out + (self.lat_comp[edit_id] * edit_value)
        return out
        