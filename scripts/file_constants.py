IMAGE_FORMATS = ('jpg', 'jpeg', 'png', 'gif')
FILE_FORMATS = ('html', 'jpg', 'jpeg', 'png', 'gif')

def get_path_from_article_data(article_id, folder_id, category_id):
    return  "posts/" + category_id + "/" + folder_id + "/" + article_id