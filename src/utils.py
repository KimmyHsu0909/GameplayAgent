import imagehash
from imagehash import ImageHash
from PIL import Image

def hash_image(img: Image) -> ImageHash:
    return imagehash.average_hash(img)

def is_same_image(img1: Image, ref_hash: ImageHash, threshold: int = 1) -> bool:
    # Hamming distance
    dist = hash_image(img1) - ref_hash
    return dist <= threshold

def is_same_hash(img_hash: ImageHash, ref_hash: ImageHash, threshold: int = 1, verbose: bool = False) -> bool:
    # Hamming distance
    dist = img_hash - ref_hash
    if verbose:
        print("Current hash dist:", dist, dist <= threshold, threshold)
    return dist <= threshold

def dist_hash(img_hash: ImageHash, ref_hash: ImageHash) -> bool:
    # Hamming distance
    dist = img_hash - ref_hash
    return dist



