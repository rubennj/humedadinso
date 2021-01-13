# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 16:20:21 2020

@author: Arash Soofi
Código para el procesamiento de los datos que se reciben de un datalogger, el archivo que se obtiene es de tipo CSV.
Los datos corresponden a las medidas realizadas por los sensores que están instalados en los mock-up (módulos Insolight) de la azotea.
"""
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

import pandas as pd
import numpy as np

from psychrochart import PsychroChart

# , guarda_ultimo_fichero_sesion
from lectura_equipos import lee_meteo


def ec_temp(v_t):
    a = 0.000854942
    b = 0.000257305
    c = 0.000000165368

    return 1/(a+b*np.log(10000/((5/v_t)-1))+c*(np.log(10000/((5/v_t)-1))**3))-273


def ec_hr(v_hum, t):
    d = -0.0000000019206
    e = 0.00001437
    f = 0.003421
    g = 0.0024

    hr = (d*(v_hum*1000)**3+e*(v_hum*1000)**2+f*(v_hum*1000))-12.4

    temp_corr = 1+(t-23)*g

    return hr / temp_corr


def ec_pres(v_p):
    # Sensor de presión -/+ 160mBar: m=64, c=-160
    # Sensor de presión -/+ 20mBar: m=8, c=-20
    m = 8
    C = -20

    return v_p*m+C


def ec_hratio(t, hr, p):
    A = 6.116441  # temo range: -20...+50°C
    m = 7.591386
    tn = 240.7263  # Triple point temperature 273.16 K

    pws = A*10**(m*t/(t+tn))  # hPa
    pw = pws*(hr/100)

    B = 621.9907  # g/kg

    return B*pw/(p-pw)


def ec_pto_rocio(hr, t):
    return ((hr/100)**(1/8))*(112+0.9*t)+(0.1*t)-112


def plot_mockup_timeseries(data_muestra_temporal, fecha):
    fig, ax_temp = plt.subplots(figsize=(15, 6))

    p1 = data_muestra_temporal.plot(ax=ax_temp, y=['temp_mod1', 'temp_mod2'],
                                    title="Set-up & Ambient variables", color=['C0'], style=['-', ':'], legend=False)

    # data_muestra_temporal.plot(ax=ax_temp, y=['temp_amb'], color=['black'], style=['-'], legend=False)
    data_muestra_temporal.plot(ax=ax_temp, y=['temp_amb'], color=[
        'black'], style=['-'], legend=False)

    data_muestra_temporal.plot(ax=ax_temp, y=['temp_front_mod1', 'temp_front_mod2'], color=[
                               'C4'], style=['-', ':'], legend=False)
    data_muestra_temporal.plot(ax=ax_temp, y=['temp_back_mod1', 'temp_back_mod2'], color=[
                               'C7'], style=['-', ':'], legend=False)
    data_muestra_temporal.plot(ax=ax_temp, y=['rocio_mod1', 'rocio_mod2'], color=[
                               'C9'], style=['-', ':'], legend=False)

    ax_rh = ax_temp.twinx()
    p2 = data_muestra_temporal.plot(ax=ax_rh, y=['hr_mod1', 'hr_mod2'], color=[
                                    'C1'], style=['-', ':'], legend=False)

    # data_muestra_temporal.plot(ax=ax_rh, y=['hr_amb'], color=['brown'], style=['-'], legend=False)
    data_muestra_temporal.plot(ax=ax_rh, y=['hr_amb'], color=[
        'brown'], style=['-'], legend=False)

    ax_pres = ax_temp.twinx()
    p3 = data_muestra_temporal.plot(ax=ax_pres, y=['pres_mod1', 'pres_mod2'], color=[
        'C2'], style=['-', ':'], legend=False)

    ax_pres.axhline(y=0, color='C2', linestyle='-', linewidth=0.3)

    ax_pres.spines['right'].set_position(('outward', 60))

    # locator = ax_temp.xaxis.set_major_locator(mdates.AutoDateLocator())
    # ax_temp.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))
    # ax_temp.xaxis.set_minor_locator(mdates.HourLocator(interval=1))
    locator = mdates.AutoDateLocator()
    formatter = mdates.ConciseDateFormatter(locator)
    ax_temp.xaxis.set_major_locator(locator)
    ax_temp.xaxis.set_major_formatter(formatter)

    ax_temp.grid(True)

    ax_temp.set_ylabel('T_Air [°C]')
    ax_temp.text(-0.06, 0.5, 'T_Front [°C]', transform=ax_temp.transAxes,
                 rotation=90, color='C4', va='center')
    ax_temp.text(-0.08, 0.5, 'T_Back [°C]', transform=ax_temp.transAxes,
                 rotation=90, color='C7', va='center')
    ax_temp.text(-0.1, 0.5, 'T_Dew [°C]', transform=ax_temp.transAxes,
                 rotation=90, color='C9', va='center')

    ax_rh.set_ylabel('RH [%]')
    ax_pres.set_ylabel('ΔP [mBar]')

    ax_temp.set_ylim([-10, 40])
    ax_rh.set_ylim([0, 105])
    ax_pres.set_ylim([-0.5, 1])

    # ejes en colores
    p1 = p1.get_lines()[0]
    p2 = p2.get_lines()[0]
    p3 = p3.get_lines()[0]

    ax_temp.yaxis.label.set_color(p1.get_color())
    ax_rh.yaxis.label.set_color(p2.get_color())
    ax_pres.yaxis.label.set_color(p3.get_color())

    ax_temp.tick_params(axis='y', colors=p1.get_color())
    ax_rh.tick_params(axis='y', colors=p2.get_color())
    ax_pres.tick_params(axis='y', colors=p3.get_color())

    # legend
    line1 = Line2D([0], [0], color='gray', linestyle='-', label='Mod. 1')
    line2 = Line2D([0], [0], color='gray', linestyle=':', label='Mod. 2')
    ax_temp.legend(handles=[line1, line2], loc='upper right')

    line3 = Line2D([0], [0], color='black', linestyle='-', label='Amb. T')
    line4 = Line2D([0], [0], color='brown', linestyle='-', label='Amb. RH')
    ax_rh.legend(handles=[line3, line4], loc='lower right')

    fig.savefig(f'graficas/{fecha}_mockups_tiempo.png')


def plot_mockup_psychro(data_muestra_psicro, fecha):
    fig, ax = plt.subplots(figsize=(12, 12))

    chart = PsychroChart('chart_style.json')
    ax = chart.plot(ax=ax)
    ax.set_title('Psychrometric chart')
    fig.suptitle(f'{fecha}')
    # cmap1 = mpl.cm.get_cmap('coolwarm')
    # cmap2 = mpl.cm.get_cmap('Oranges')

    # rango = data_muestra_psicro.index.day.unique()

    data_muestra_psicro.plot(ax=ax, x='temp_mod1', y='h_ratio1',
                             marker='o', color='black', alpha=1)
    data_muestra_psicro.plot(ax=ax, x='temp_mod2', y='h_ratio2',
                             marker='o', color='white', alpha=1)
    data_muestra_psicro.plot(ax=ax, x='temp_amb', y='h_ratio_amb',
                             marker='o', color='red', alpha=1)

    for mom in data_muestra_psicro.index:

        # norm = mpl.colors.TwoSlopeNorm(vmin=data_muestra_psicro['pres_mod1'].min(), vcenter=0, vmax=data_muestra_psicro['pres_mod1'].max())
        # sm = mpl.cm.ScalarMappable(norm=norm, cmap=cmap1)

        # ax.plot(temp1, h_ratio1, marker='o', color='black', alpha=1) # sm.to_rgba(pres1)
        # sm = ax.scatter(temp1, h_ratio1, c=pres1, s=20, cmap=cmap1, norm=norm, marker='o')
        # ax.plot(temp2, h_ratio2, marker='o', color='white', alpha=1) # cmap2(pos_color)

        if mom.minute == 0:
            ax.text(x=data_muestra_psicro['temp_mod1'][mom], y=data_muestra_psicro['h_ratio1']
                    [mom], s=mom.hour, fontsize=8, color='white')
            ax.text(x=data_muestra_psicro['temp_mod2'][mom], y=data_muestra_psicro['h_ratio2']
                    [mom], s=mom.hour, fontsize=8, color='black')

    # cbar = plt.colorbar(sm, ax=ax)
    # cbar.set_label('P [mBar]')

    dot1 = Line2D([0], [0], color='black', marker='o',
                  linestyle='None', label='Mod. 1')
    dot2 = Line2D([0], [0], color='white', marker='o',
                  linestyle='None', label='Mod. 2', markeredgecolor='black')
    dot3 = Line2D([0], [0], color='red', marker='o',
                  linestyle='None', label='Ambient')
    ax.legend(handles=[dot1, dot2, dot3], loc='upper left')

    ax.set_xlabel(r'Internal air temperature [$°C$]')
    ax.set_ylabel(r'Humidity ratio [$g_w / kg_{da}$]')

    ax.set_ylim([0, 20])
    ax.set_xlim([-5, 30])

    fig.savefig(f'graficas/{fecha}_mockups_psicrom.png')

    # cax = fig.add_axes([0.27, 0.8, 0.5, 0.05])

    # im = ax.imshow(data, cmap='viridis')
    # fig.colorbar(im, cax=cax, orientation='horizontal')
    # sm = plt.cm.ScalarMappable(cmap='viridis', norm=plt.Normalize(vmin=0, vmax=1))
    # cbar = plt.colorbar(sm)
    # cbar.set_ticklabels([])


def procesa_señales(data):
    data_proces = pd.DataFrame()

    data_proces['temp_mod1'] = ec_temp(v_t=data['CH1:M1-TEMP'])
    data_proces['temp_mod2'] = ec_temp(v_t=data['CH3:M2-TEMP'])
    data_proces['temp_amb'] = ec_temp(v_t=data['CH5:C-TEMP'])

    data_proces['hr_mod1'] = ec_hr(
        v_hum=data['CH2:M1-RH'], t=data_proces['temp_mod1'])
    data_proces['hr_mod2'] = ec_hr(
        v_hum=data['CH4:M2-RH'], t=data_proces['temp_mod2'])

    data_proces.loc[data_proces['hr_mod2'] > 100] = 100
    data_proces.loc[data_proces['hr_mod2'] < 0] = 0

    data_proces['hr_amb'] = ec_hr(
        v_hum=data['CH6:C-RH'], t=data_proces['temp_amb'])

    data_proces['pres_mod1'] = ec_pres(v_p=data['CH8:M1-SP'])
    data_proces['pres_mod2'] = ec_pres(v_p=data['CH7:M2-SP'])

    data_proces['temp_front_mod1'] = data['CH9:M1-Tp FS']
    data_proces['temp_front_mod2'] = data['CH11:M2-Tp FS']

    data_proces['temp_back_mod1'] = data['CH10:M1-Tp BS']
    data_proces['temp_back_mod2'] = data['CH12:M2-TP BS']

    data_proces['rocio_mod1'] = ec_pto_rocio(
        hr=data_proces['hr_mod1'], t=data_proces['temp_mod1'])
    data_proces['rocio_mod2'] = ec_pto_rocio(
        hr=data_proces['hr_mod2'], t=data_proces['temp_mod2'])

    pres = 940  # 101325 hPa

    data_proces['h_ratio1'] = ec_hratio(
        t=data_proces['temp_mod1'], hr=data_proces['hr_mod1'], p=pres)
    data_proces['h_ratio2'] = ec_hratio(
        t=data_proces['temp_mod2'], hr=data_proces['hr_mod2'], p=pres)

    # lee estacion
    data_meteo = lee_meteo(data_proces.index.round('T'))
    data_meteo.index = data_proces.index

    data_meteo = data_meteo.rename(
        columns={'Temp. Ai 1': 'temp_amb', 'Hum. Rel': 'hr_amb'})

    data_meteo['h_ratio_amb'] = ec_hratio(
        t=data_meteo['temp_amb'], hr=(data_meteo['hr_amb']), p=pres)

    # axz = data_proces[['h_ratio1', 'h_ratio2']].plot();
    # data_meteo['h_ratio_amb'].plot(ax=axz)
    # data_meteo[['h_ratio_amb', 'Lluvia', 'Limpieza']].plot()

    data_proces['h_ratio_amb'] = data_meteo['h_ratio_amb']
    data_proces['temp_amb'] = data_meteo['temp_amb']
    data_proces['hr_amb'] = data_meteo['hr_amb']
    data_proces['Gh'] = data_meteo['Gh']
    data_proces['G(41)'] = data_meteo['G(41)']

    return data_proces
