import matplotlib.pyplot as plt
from matplotlib.dates import ConciseDateFormatter, AutoDateLocator
plt.rcParams['timezone'] = 'America/Mexico_City'    

def plot_T_I(dia):
    fig, ax = plt.subplots(2,figsize=(10,6),sharex=True)

    df = dia.iloc[::600]
    ax[0].plot(df.Ta, 'k-',label='Ta')
    # ax[0].plot(df.Tn, 'g-',label='Tn')
    ax[0].plot(df.Tsa,'r-',label='Tsa')
    ax[0].fill_between(df.index,
                    df.Tn + df.DeltaTn,
                    df.Tn - df.DeltaTn,color='green',alpha=0.3)

    ax[1].plot(df.Ig,label='Ig')
    ax[1].plot(df.Ib,label='Ib')
    ax[1].plot(df.Id,label='Id')
    ax[1].plot(df.Is,label='Is')

    ax[0].set_ylabel('Temperatura [$^oC$]')
    ax[1].set_ylabel('Irradiancia [$W/m^2$]')

    locator = AutoDateLocator()
    formatter = ConciseDateFormatter(locator)
    ax[1].xaxis.set_major_formatter(formatter)


    for a in ax:
        a.legend()
        a.grid()
    fig.tight_layout()