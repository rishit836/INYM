import argparse
import numpy as np
import os
from PIL import Image

from scipy.fftpack import dct


parser = argparse.ArgumentParser(description="standalone running script on files.")

parser.add_argument("--image")
parser.add_argument("--img1")
parser.add_argument("--img2")

args =parser.parse_args()

# converts the binary hash bits data to hex 
def convert_binary_to_hex(binary_array):
    hex_str = ""
    for i in range(0, len(binary_array), 4):
        nibble = binary_array[i:i+4]
        val = 0
        for bit in nibble:
            val = (val << 1) | bit
        hex_str += format(val, 'x')
    return hex_str

def get_p_hash(image_path):
    if not os.path.exists(image_path):
        return "INVALID IMAGE PATH"
    
    # open the image in grayscale (luminance mode - L)
    img = Image.open(image_path).convert('L')
    
    # resize the image to 32 X 32 using LANCZOS method for quality downsizing.
    img = img.resize((32,32),Image.Resampling.LANCZOS)

    # converting the image into pixel numpy array
    pixels = np.array(img)

    # computing DCT (discrete cosine term)
    # applying once for one axis
    dct_data = dct(pixels, type=2, axis=0, norm="ortho")
    # applying twice for second axis
    dct_data = dct(dct_data, type=2, axis=1,norm="ortho")

    # extracting the top 8X8 as they contain low frequency (image data) and the other
    # half contains noise so we can exclude that
    dct_low_freq = dct_data[:8,:8]

    # computing average of the frequency and removing the first term because it contains data about brightness of the image 
    # which is irrelevant
    dct_low_freq_flat = dct_low_freq.flatten()
    average = (np.sum(dct_low_freq_flat)-dct_low_freq[0,0])/63

    # compting the binary hash bits (64 bits)
    hash_bits = []
    for x in range(8):
        for y in range(8):
            if dct_low_freq[x,y]>average:
                hash_bits.append(1)
            else:
                hash_bits.append(0)

    return hash_bits

def hamming_distance(hash1, hash2):
    # Assuming hash1 and hash2 are lists of 64 bits (0s and 1s)
    if len(hash1) != len(hash2):
        raise ValueError("Hashes must be of equal length")
        
    return sum(b1 != b2 for b1, b2 in zip(hash1, hash2))
def get_dist(image_1_path,image_2_path):
    img_1_phash = get_p_hash(image_1_path)
    img_2_phash = get_p_hash(image_2_path)

    dist = hamming_distance(img_1_phash,img_2_phash)

    return dist

if __name__ == "__main__":
    img1,img2 = args.img1,args.img2
    
    if get_dist(img1,img2)<=12:
        print("images are same")
    else:
        print("images are different.")
