import numpy as np
from astropy import units as u
from ctapipe.instrument import CameraGeometry
from ctapipe.instrument.camera import _find_neighbor_pixels, \
    _get_min_pixel_seperation
from numpy import median
import pytest


def test_load_by_name():

    cams = CameraGeometry.get_known_camera_names()
    assert len(cams) > 4
    assert 'FlashCam' in cams
    assert 'NectarCam' in cams
    

    for cam in cams:
        geom = CameraGeometry.from_name(cam)



def test_make_rectangular_camera_geometry():
    geom = CameraGeometry.make_rectangular()
    assert(geom.pix_x.shape == geom.pix_y.shape)


def test_load_hess_camera():
    geom = CameraGeometry.from_name("LSTCam")
    assert len(geom.pix_x) == 1855


def test_guess_camera():
    px = np.linspace(-10, 10, 11328) * u.m
    py = np.linspace(-10, 10, 11328) * u.m
    geom = CameraGeometry.guess(px, py,0 * u.m)
    assert geom.pix_type.startswith('rect')


def test_get_min_pixel_seperation():
    x, y = np.meshgrid(np.linspace(-5, 5, 5), np.linspace(-5, 5, 5))
    pixsep = _get_min_pixel_seperation(x.ravel(), y.ravel())
    assert(pixsep == 2.5)


def test_find_neighbor_pixels():
    x, y = np.meshgrid(np.linspace(-5, 5, 5), np.linspace(-5, 5, 5))
    neigh = _find_neighbor_pixels(x.ravel(), y.ravel(), rad=3.1)
    assert(set(neigh[11]) == set([16, 6, 10, 12]))

def test_neighbor_pixels():
    hexgeom = CameraGeometry.from_name("LSTCam")
    recgeom = CameraGeometry.make_rectangular()

    # most pixels should have 4 neighbors for rectangular geometry and 6 for
    # hexagonal
    assert int(median(recgeom.neighbor_matrix.sum(axis=1))) == 4
    assert int(median(hexgeom.neighbor_matrix.sum(axis=1))) == 6

def test_to_and_from_table():
    geom = CameraGeometry.from_name("LSTCam")
    tab = geom.to_table()
    geom2 = geom.from_table(tab)

    assert geom.cam_id == geom2.cam_id
    assert (geom.pix_x == geom2.pix_x).all()
    assert (geom.pix_y == geom2.pix_y).all()
    assert (geom.pix_area == geom2.pix_area).all()
    assert geom.pix_type == geom2.pix_type


def test_write_read(tmpdir):

    filename = str(tmpdir.join('testcamera.fits.gz'))

    geom = CameraGeometry.from_name("LSTCam")
    geom.to_table().write(filename, overwrite=True)
    geom2 = geom.from_table(filename)

    assert geom.cam_id == geom2.cam_id
    assert (geom.pix_x == geom2.pix_x).all()
    assert (geom.pix_y == geom2.pix_y).all()
    assert (geom.pix_area == geom2.pix_area).all()
    assert geom.pix_type == geom2.pix_type

def test_known_cameras():
    cams = CameraGeometry.get_known_camera_names()
    assert 'FlashCam' in cams
    assert len(cams) > 3


def test_precal_neighbors():
    geom = CameraGeometry(cam_id="TestCam",
                          pix_id=np.arange(3),
                          pix_x=np.arange(3)*u.deg,
                          pix_y=np.arange(3)*u.deg,
                          pix_area=np.ones(3)*u.deg**2,
                          neighbors=[[1,],[0,2],[1,]],
                          pix_type='rectangular',
                          pix_rotation="0deg",
                          cam_rotation="0deg" )

    neigh = geom.neighbors
    assert len(neigh) == len(geom.pix_x)

    nmat = geom.neighbor_matrix
    assert nmat.shape == (len(geom.pix_x), len(geom.pix_x))



def test_slicing():
    geom = CameraGeometry.from_name("NectarCam")
    sliced1 = geom[100:200]

    assert len(sliced1.pix_x) == 100
    assert len(sliced1.pix_y) == 100
    assert len(sliced1.pix_area) == 100
    assert len(sliced1.pix_id) == 100

    sliced2 = geom[[5,7,8,9,10]]
    assert sliced2.pix_id[0] == 5
    assert sliced2.pix_id[1] == 7
    assert len(sliced2.pix_x) == 5
if __name__ == '__main__':
    pass
