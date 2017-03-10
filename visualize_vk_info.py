import matplotlib.pyplot as plt

from vkapi import VKApi
    

def plot_stats(years, w_years, m_years, genders):
    labels = 'Women', 'Men'
    explode = (0.1, 0)  # only "explode" the 1st slice
    
    fig1, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, sharex='none', sharey='none')
    ax1.pie(genders, explode=explode, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)    

    axes = [ax2, ax3, ax4]
    dif_years = [years, w_years, m_years]
    titles = ["All ages", "Women's age", "Men's age"]

    for i in range(len(axes)):
        if len(dif_years[i]) != 0:
            bins = max(dif_years[i]) - min(dif_years[i])
            if bins == 0:
                bins = 1
            axes[i].hist(dif_years[i], bins, facecolor='green', alpha=0.75)
            axes[i].set_title(titles[i])
            axes[i].grid(True)
       
    plt.show()


def main():
    login, password = '', ''
    vk = VKApi(login, password)

    url = 'https://vk.com/search?c[section]=people&c[group]=39500620'
     
    users = vk.get_users_from_url(url)
    years, w_years, m_years, genders = vk.get_info(users, 1980)
    plot_stats(years, w_years, m_years, genders)
        

if __name__ == '__main__':
    main()


