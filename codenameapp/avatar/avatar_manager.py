import logging
from pathlib import Path

import numpy as np
from flask import send_from_directory, make_response

logger = logging.getLogger(__name__)

AVATAR_FOLDER_WEIGHTS = {
    Path("static/icons/avatars/svg"): 0,
    Path("static/icons/avatars-with-medical-masks/svg"): 1,
    Path("static/icons/crime-protection/svg"): 2,
    Path("static/icons/people-avatars/svg"): 4,
    Path("static/icons/profession-avatars/svg"): 4,
    Path("static/icons/services/svg"): 5,
    Path("static/icons/sport-avatars/svg"): 5,
}


class AvatarManager:
    def init_routes(self, app):
        app.add_url_rule("/avatar/random", view_func=self.get_random_avatar_img)
        app.add_url_rule("/avatar/download/<path:rel_path>", view_func=self.download_avatar_img)

    @staticmethod
    def choose_random_avatar_img() -> Path:
        files, weights = [], []
        for folder, weight in AVATAR_FOLDER_WEIGHTS.items():
            paths = list(folder.glob("*.svg"))
            files += paths
            weights += [weight] * len(paths)
        weights = np.array(weights) / sum(weights)
        img = np.random.choice(files, p=weights)
        return img

    def get_random_avatar_img(self):
        img_path = self.choose_random_avatar_img()
        logger.debug(f"Path to img: {img_path.relative_to('static').as_posix()}")
        resp = make_response({"id": img_path.relative_to("static/icons").as_posix(),
                                "url": img_path.relative_to('.').as_posix()})
        resp.cache_control.no_cache = True  # Disable caching
        return resp

    def download_avatar_img(self, rel_path):
        logger.debug(f"Download requested for img: {rel_path}")
        img_path = Path("static") / Path(rel_path)
        icons_folder = Path("static/icons").resolve()
        # Make sure that we're not accessing some other folder
        img_path = icons_folder / img_path.resolve().relative_to(icons_folder)
        resp = send_from_directory("static", img_path.relative_to(icons_folder.parent).as_posix())
        resp.cache_control.public = True  # Allow caching
        return
