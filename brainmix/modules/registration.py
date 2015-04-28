import os, glob
import numpy as np
from skimage import feature
from skimage import io
from skimage import transform as tf
import matplotlib.pyplot as plt
from skimage.color import gray2rgb


# -----------------Registration function-------------------------


def reg(src, dst):
    """Takes in a source and destination image and returns a
    registered source image.
    """
    shifts, err, phasediff = feature.register_translation(src, dst)
    tform = tf.AffineTransform(translation=shifts)
    reg_dst = tf.warp(dst, inverse_map=tform.inverse)

    return reg_dst

# ----------------Stack function --------------------------------


def reg_iter(stack):
    """
    input: a stack of images and registers each one using the first
    image as the destination.
    output: a registered stack.
    """
    dst = stack[0]
    reg_stack = [reg(src, dst) for src in stack]
    return reg_stack

# --------------View overlayed result--------------------------


def overlay_pics(src, dst):

    image0_ = src
    image1_ = dst

    def add_alpha(image, background=-1):
        """Add an alpha layer to the image.

        The alpha layer is set to 1 for foreground
        and 0 for background.
        """
        rgb = gray2rgb(image)
        alpha = (image != background)
        return np.dstack((rgb, alpha))

    image0_alpha = add_alpha(image0_)
    image1_alpha = add_alpha(image1_)

    merged = (image0_alpha + image1_alpha)
    alpha = merged[..., 3]

    # The summed alpha layers give us an indication of
    # how many images were combined to make up each
    # pixel.  Divide by the number of images to get
    # an average.
    merged /= np.maximum(alpha, 1)[..., np.newaxis]
    return merged

# ---------------main-------------------------------


def registration(img_stack):
    """input: ndarray of images
    ouput: ndarray of registered images
    """
    reg_stack = reg_iter(img_stack)

    if not np.array_equal(img_stack[0], reg_stack[0]):
        print("destination image has been changed in registered stack.")
    # src and dst images should be different
    assert not np.array_equal(img_stack[0], reg_stack[1])
    return io.concatenate_images(reg_stack)

if __name__ == "__main__":
    # ------------------Create input ndarray------------------------
    inputDir = '../data/test/'
    imageFiles = glob.glob(os.path.join(inputDir, '*.jpg'))
    imageVolume = io.ImageCollection(imageFiles, as_grey=True).concatenate()
    stack = imageVolume

    reg_stack = registration(stack)

    print('stack is of type', type(stack))
    print('stack dimensions are', stack.shape)
    print('registered stack is of type', type(reg_stack))
    print('registered stack dimensions are', reg_stack.shape)

    merged = [overlay_pics(stack[0], img) for img in stack]
    merged_reg = [overlay_pics(reg_stack[0], img) for img in reg_stack]
    fig, ax = plt.subplots(nrows=2, ncols=3, figsize=(8, 5))

    plt.gray()

    ax[0, 0].imshow(merged[0])
    ax[0, 0].axis('off')
    ax[0, 0].set_title('original 1-1')
    ax[0, 1].imshow(merged[1])
    ax[0, 1].axis('off')
    ax[0, 1].set_title('original 1-2')
    ax[0, 2].imshow(merged[2])
    ax[0, 2].axis('off')
    ax[0, 2].set_title('original 1-3')

    ax[1, 0].imshow(merged_reg[0])
    ax[1, 0].axis('off')
    ax[1, 0].set_title('registered 1-1')
    ax[1, 1].imshow(merged_reg[1])
    ax[1, 1].axis('off')
    ax[1, 1].set_title('registered 1-2')
    ax[1, 2].imshow(merged_reg[2])
    ax[1, 2].axis('off')
    ax[1, 2].set_title('registered 1-3')

    fig.subplots_adjust(wspace=0.02, hspace=0.2,
                        top=0.9, bottom=0.05, left=0, right=1)

    plt.show()
