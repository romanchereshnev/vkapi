import vk_api

class VKApi(object):
    """ Simple vk api for getting some information from different vk sources
        Attributes:
            vk - vk session 
        Methods:
            user_have_year - is user have year of bith in user info
            get_user_year - get user year from user info
            get_friends - get friends from users
            chunks - separate list by several samller lists
            delete_years_lover_than - delete years from list lover thatn threashold
            get_ids_strings - create list of strings from list of ids
            get_info - get infromation from useds id
            get_users_in_group - get users from goup
    """

    def __init__(self, login, password):
        """ Initialize VK api.
            Input:
                login: string
                    email or phone number of user
                password:
                    password from vk account
        """
        vk_session = vk_api.VkApi(login, password)
        try:
            vk_session.authorization()
        except vk_api.AuthorizationError as error_msg:
            print(error_msg)
        self.vk = vk_session.get_api()   

    def user_have_year(self, user):
        """ Is there year of birth in user info
            Input: 
                user: dict
                    dict with user info. More in: https://vk.com/dev/objects/user
            Output:
                bool:
                    True if there is year in user info
        """
        return 'bdate' in user and len(user['bdate'].split(".")[-1]) == 4

    def get_user_year(self, user):
        """ Get birth year from user info
            Input: 
                user: dict
                    dict with user info. More in: https://vk.com/dev/objects/user
            Output:
                int:
                    Year of birth or None if there is no year in user info
        """
        if self.user_have_year(user):
            return int(user['bdate'].split(".")[-1])
        else:
            return None

    def get_friends(self, user_id=None, fields='sex,bdate'):
        """ Get frinds id from user_id. If user not defined, freinds ara taken from authorize user
            Input: 
                user_id: int
                    id of user, from whome gets frinds id
                fields: string
                    string of fields. See more in https://vk.com/dev/objects/user
        """
        if user_id is None:
            friends_info = self.vk.friends.get(fields=fields)
        else:
            friends_info = self.vk.friends.get(fields=fields, user_id=user_id)
        return friends_info['items']

    def chunks(self, big_list, n):
        """ Separate list in several lists with length n
            Input:
                big_list: list
                    Big list, needs to separated
                n: int
                    leangth of new list
            Output:
                List of lenght n
        """
        for i in range(0, len(big_list), n):
            yield big_list[i:i + n]

    def delete_years_lover_than(self, years, w_years, m_years, threashold_year):
        """ Remove years from lists lower than threashold_year
            Input:
                years: list of ints
                    List of year of all user     
                w_years: list of ints
                    List of year of women user
                m_years: list of ints
                    List of year of men user
                threashold_year: int
                    Threashold year
            Output: 
                set in form (years, w_years, m_years)
                    Threasholded lists               
        """
        years   = [year for year in years if year >= threashold_year]
        w_years = [year for year in w_years if year >= threashold_year]
        m_years = [year for year in m_years if year >= threashold_year]
        return years, w_years, m_years

    def get_ids_strings(self, ids):
        """ Split id list by list of strings ids with length oof 1000. This is requriment of vk api.
            Input:
                ids: list of int
                    list of id of users
            Output:
                list of strings
                    each element contains no more than 1000 ids separated by comma
        """
        #Split ids by list no longer than 1000 units,
        #because vk api can only gets 1000 ids per one call 
        splitted_ids = list(self.chunks(ids, 1000))
        ids_in_list = []
        
        #crate list of strings with ids
        for split_ids in splitted_ids:
            user_ids = ''
            #make string ids list. Do it because of api requirement
            for id in split_ids:
                user_ids += str(id) + ","
            #remove last ","
            user_ids = user_ids[:-1]
            ids_in_list.append(user_ids)

        return ids_in_list

    def get_info(self, ids, threashold_year = None):
        """ Get information from list of ids
            Input:
                ids: int list
                    List of users id
                threashold_year: int
                    Threashold year
            Output:
                set in format (years, w_years, m_years, genders)
                    years: list of years of all users
                    w_years: list of years of women users
                    m_years: list of years of men users
                    genders: list of length 2. 
                        First element is number of women
                        Second - number of men.
        """
        
        ids_in_list = self.get_ids_strings(ids)

        users = []
        # get users by no more than 1000 users per call
        for user_ids in ids_in_list:
            users += self.vk.users.get(user_ids=user_ids, fields='sex,bdate')

        years = []                      # Years of all users
        w_years = []                    # Years of women users
        m_years = []                    # Years of men users
        genders = [0, 0]                # Number of women and men in user 
        gen_list = [w_years, m_years]
        for user in users:
            # 1 - i women, 2 is men.
            if 'sex' in user:
                genders[user['sex']-1] += 1
            if self.user_have_year(user):
                years.append(self.get_user_year(user))
            if 'sex' in user and self.user_have_year(user):
                gen_list[user['sex']-1].append(self.get_user_year(user) )
    
        if threashold_year is not None:
            years, w_years, m_years = self.delete_years_lover_than(years, w_years, m_years, threashold_year)
        return years, w_years, m_years, genders
   
    def get_users_in_group(self, group_id):
        """ Get users in group
            Input:  
                group_id - int
                    id of vk group
            Output:
                list of users id in group
        """
        members = self.vk.groups.getMembers(group_id=group_id, count=1)
        peoples = members['count']
        ids = []
        while len(ids) < peoples:
            members = self.vk.groups.getMembers(group_id=group_id, offset=len(ids))
            ids += members['items']

        return ids

    def get_users_from_likes(self, type, owner_id, item_id):
        """ Get users who like something
            Input:  
                type: string
                    typpe of post
                owner_id: int
                    id of owner
                item_id: int
                    item id
            Output:
                list of users id
        """
        likes = self.vk.likes.getList(type=type, owner_id=owner_id, item_id=item_id, count=1)
        likes = self.vk.likes.getList(type=type, owner_id=owner_id, item_id=item_id, count=likes['count'])
        return likes['items']

    def get_users_from_url(self, url):
        """ Get users by url. You can get users from:
                Group, user who like photo, users who like post, users who like video
            Input:  
                url: string
                    url of vk page
            Output:
                list of users id
        """

        if 'vk' not in url:
            raise RuntimeError("Strange url")
        
        if 'photo' in url:  #https://vk.com/fakebusters?z=photo-39500620_456244578%2Falbum-39500620_00%2Frev
                            #https://vk.com/romanchereshnev?z=photo95357292_393830601%2Falbum95357292_0%2Frev
            ids = (url.split("%")[0]).split("=photo")[-1].split("_")
            owner_id = int(ids[0])
            item_id = int(ids[1])
            users = self.get_users_from_likes(type='photo', owner_id=owner_id, item_id=item_id)       
        elif 'wall' in url: #https://vk.com/fakebusters?w=wall-39500620_297855
                            #https://vk.com/romanchereshnev?w=wall95357292_378
            ids = (url.split("=wall")[-1]).split("_")
            owner_id = int(ids[0])
            item_id = int(ids[1])
            users = self.get_users_from_likes(type='post', owner_id=owner_id, item_id=item_id)
        elif 'video' in url: #https://vk.com/video?z=video95357292_456239134%2Fpl_cat_updates
                             #https://vk.com/videos-90074084?z=video-90074084_456239586%2Fclub90074084%2Fpl_-90074084_-2
            ids = ((url.split("%")[0]).split("=video")[-1]).split("_")
            owner_id = int(ids[0])
            item_id = int(ids[1])
            users = self.get_users_from_likes(type='video', owner_id=owner_id, item_id=item_id)
        if 'group' in url:  #https://vk.com/search?c[section]=people&c[group]=39500620
            group_id = int(url.split('=')[-1])
            users = self.get_users_in_group(group_id)
        return users