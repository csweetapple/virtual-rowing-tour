#!/usr/bin/env python3
# -*- coding: utf-8 -*-


def kml2latlon(ifile):
    """Read lon lat from kml file with single path"""
    from fastkml import kml, geometry

    with open(ifile, 'rt') as myfile:
        doc = myfile.read()
    k = kml.KML()
    k.from_string(doc.encode("utf-8"))
    f = list(k.features())
    g = list(f[0].features())[0].geometry

    lat = []
    lon = []
    for c in g.coords:
        lon.append(c[0])
        lat.append(c[1])

    return lat, lon


def read_logbook(ifile, startdate=None, enddate=None):
    import pandas

    df = pandas.read_csv('log/rowing.log', sep=' *; *')
    distance = df['meter'].sum(axis=0)
    last_date = df['date'].values[-1]

    return distance, last_date


def travel(distance, lat_route, lon_route):
    import numpy as np
    from geopy import distance as geodis

    latlon = tuple(zip(lat_route, lon_route))
    s_vec = np.empty(len(lat_route))
    s_sum = np.empty(len(lat_route))
    s_vec[:] = np.NaN
    s_sum[:] = np.NaN
    for n in range(len(lat_route)):
        if n == 0:
            s_vec[n] = 0.0
            s_sum[n] = 0.0
        else:
            s_vec[n] = geodis.distance(latlon[n], latlon[n-1]).m
            s_sum[n] = s_vec[n] + s_sum[n-1]

    # Find position of boat and the remaining distance
    # traveled  beyond last resolved waypoint
    lat_pos = lat_route[0]
    lon_pos = lon_route[0]
    for n in range(len(s_sum)):
        if s_sum[n] > distance:
            lat_pos = lat_route[n-1]
            lon_pos = lon_route[n-1]
            res = distance - s_sum[n-1]
            break

    # ToDo: Correct position by travelling the distance res
    #       from the last know position (lat_pos, lon_pps)

    return lat_pos, lon_pos, s_sum[n-1], s_sum[-1]


def main():

    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    import cartopy.feature as cf
    from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

    name_start = "Exmouth"
    name_finish = "La Gomera"
    ifile_kml = "routes/Exmouth_La_Gomera.kml"
    first_date = '2020-10-31'

    lat_route, lon_route = kml2latlon(ifile_kml)

    distance, last_date = read_logbook("log/rowing.log",
                                       startdate=first_date,
                                       enddate="2020-10-31")

    lat_boat, lon_boat, d1, d2 = travel(distance, lat_route, lon_route)

    extent1 = [-20, 2.5, 25, 52.5]
    extent2 = [-6,   -2, 47.25, 51]
    proj = ccrs.PlateCarree()

    fig = plt.figure(figsize=(10, 8))
    fig.suptitle(name_start + ' to ' + name_finish
                 + '({:.0f} km)'.format(d2/1000.) + ' \n'
                 + first_date + ' - ' + last_date)

    land_10m = cf.NaturalEarthFeature('physical',
                                      'land', '10m',
                                      edgecolor='face',
                                      facecolor=cf.COLORS['land'])

    lon_formatter = LongitudeFormatter(zero_direction_label=True)
    lat_formatter = LatitudeFormatter()

    ax1 = fig.add_subplot(1, 2, 1, projection=proj)
    ax1.set_extent(extent1, crs=proj)
    # ax1.coastlines(resolution='50m')
    ax1.add_feature(land_10m)
    ax1.set_xticks([-20, -15, -10, -5, 0, 5])
    ax1.set_yticks([25, 30, 35, 40, 45, 50])
    ax1.xaxis.set_major_formatter(lon_formatter)
    ax1.yaxis.set_major_formatter(lat_formatter)
    ax1.plot(lon_route[0], lat_route[0], marker='o', color='blue',
             markersize=4, alpha=0.7, transform=proj)
    ax1.plot(lon_route[-1], lat_route[-1], marker='o', color='blue',
             markersize=4, alpha=0.7, transform=proj)
    ax1.plot(lon_route, lat_route, ':', transform=proj)
    ax1.plot(lon_boat, lat_boat, marker='o', color='red',
             markersize=8, alpha=0.7, transform=proj)
    ax1.set_title('Distance from ' + name_start + ': '
                  + '{:.0f} km'.format(d1/1000.))

    ax2 = fig.add_subplot(1, 2, 2, projection=proj)
    ax2.add_feature(land_10m)
    ax2.set_xticks([-20, -15, -10, -6, -5, -4, -3, 0, 5])
    ax2.xaxis.set_major_formatter(lon_formatter)
    ax2.set_yticks([25, 30, 35, 40, 45, 46, 47, 48, 49, 50, 51])
    ax2.yaxis.set_major_formatter(lat_formatter)
    ax2.plot(lon_route[0], lat_route[0], marker='o', color='blue',
             markersize=4, alpha=0.7, transform=proj)
    ax2.plot(lon_route[-1], lat_route[-1], marker='o', color='blue',
             markersize=4, alpha=0.7, transform=proj)
    ax2.plot(lon_route, lat_route, ':', transform=proj)
    ax2.plot(lon_boat, lat_boat, marker='o', color='red',
             markersize=8, alpha=0.7, transform=proj)
    ax2.set_title('Navigation chart')
    ax2.set_extent(extent2)

    # plt.show()
    plt.savefig("plots/Exmouth_RC_virtual_row_winter_2020--2021.png")


if __name__ == "__main__":
    main()
