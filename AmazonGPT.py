import openai
import requests
from bs4 import BeautifulSoup
from collections import Counter
from rich import print
from rich.text import Text


openai.api_key = "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"

main_url = input("URL: ")
reviewlist = []
aboutlist= []
reviews = []



def get_professional_text(output):
    # Prompt the user for input
    

    # Create a Text object with the user input
    text = Text(output)

    # Apply formatting to the Text object
    text.stylize("bold")
    text.stylize("underline")

    # Create the professional-looking output
    output = f"""
    [red]---------------------------------------------------
                        AI Consultant
    ---------------------------------------------------[/red]

    {output}

    [red]---------------------------------------------------
                            END
    ---------------------------------------------------[/red]
    """

    return output

def get_product_title(main_soup):
    try:
        product_title = main_soup.find('span', {'id' : 'productTitle'})
        product_title = product_title.text.strip()
        return product_title
    except:
        pass

def convert_to_review_link(main_url):
    product_id = main_url.split("/dp/")[1].split("/")[0]
    review_url = f"https://www.amazon.com/{product_id}/product-reviews/{product_id}/ref=cm_cr_getr_d_paging_btm_prev_1?ie=UTF8&reviewerType=all_reviews&pageNumber=1"
    return review_url



def get_review_soup(review_url):
    
    r = requests.get('http://localhost:8050/render.html' , params = {'url': review_url, 'wait': 2})
    review_soup = BeautifulSoup(r.text, 'html.parser')
    return review_soup

def get_main_soup(main_url):
    
    r = requests.get('http://localhost:8050/render.html' , params = {'url': main_url, 'wait': 2})
    main_soup = BeautifulSoup(r.text, 'html.parser')
    return main_soup

def get_reviews(review_soup):

    reviews = review_soup.find_all('div',{'data-hook': 'review'})
    try:
        for item in reviews:
            review = {
                'product': review_soup.title.text.replace('Amazon.com: Customer reviews:', '').strip(),
                'title': item.find('a',{'data-hook': 'review-title'}).text.strip(),
                'rating': float(item.find('i',{'data-hook':'review-star-rating'}).text.replace('out of 5 stars','').strip()),
                'body': item.find('span',{'data-hook': 'review-body'}).text.strip()[:100]
            }
            reviewlist.append(review)
    except:
        pass
    
def get_price(main_soup):
    try:
        price_span = main_soup.find('span',{'class': 'a-price-whole'})
        price = (price_span.text.replace('.','').strip())
    
        return price
    except:
        pass

def get_productDescription(main_soup):
    description = main_soup.find('div', {'id': 'productDescription'})
    if description is not None:
        product_description = description.find('span').text.strip()
        return product_description
    return ""


def get_about_this_item(main_soup):
    try:
        about_items = main_soup.find_all('div', {'id': 'feature-bullets'})
        
        for item in about_items:
            about_this_item_elements = item.find_all('span', {'class': 'a-list-item'})
            for element in about_this_item_elements:
                about_this_item = element.text.strip()
                aboutlist.append(about_this_item)
        return aboutlist
    except:
        pass

            
    

####MAIN CODE






review_url = convert_to_review_link(main_url)
review_soup = get_review_soup(review_url)
main_soup = get_main_soup(main_url)


        




for x in range(1,2):
    review_url_without_page = review_url.split('pageNumber=')[0]
    review_url_moving = review_url_without_page + 'pageNumber=' + str(x)
    paged_review_soup = get_review_soup(review_url_moving)
    print(f'Getting page: {x}')
    get_reviews(paged_review_soup)
    if not paged_review_soup.find('li', {'class' : 'a-disabled a-last'}):
        pass
    else:
        break



product_description = get_productDescription(main_soup)
about_this_item = get_about_this_item(main_soup)
price = get_price(main_soup)
product_title = get_product_title(main_soup)
print("...")
'''print("Product Title:")
print(product_title)

print("Product Description:")
print(product_description)

print("\nAbout This Item:")
for i, bullet in enumerate(about_this_item):
    print(f"{i+1}. {bullet}")

print("\nItem Price:")
print("$" + price)

for i, review in enumerate(reviewlist, start=1):
    review_text = f"{i}. Review Subject: '{review['title']}', Rating out of 5 stars: '{review['rating']}', Review: '{review['body']}'."
    reviews.append(review_text)

reviews_text = "\n".join(reviews)
print("Reviews:")
#print(reviews_text)'''
print("...")


result = ""
result += "Product Title:\n" + product_title + "\n\n"
result += "Product Description:\n" + product_description + "\n\n"
result += "About This Item:\n"
for i, bullet in enumerate(about_this_item, start=1):
    result += f"{i}. {bullet}\n"
result += "\nItem Price:\n" + "$" + price + "\n\n"
result += "Reviews:\n"
for i, review in enumerate(reviewlist, start=1):
    review_text = f"{i}. Review Subject: '{review['title']}', Rating out of 5 stars: '{review['rating']}', Review: '{review['body']}'."
    result += review_text + "\n"


 #Generate suggestions using ChatGPT



prompt = (
"ChatGPT, as the manager of an eCommerce store, I seek your expertise in improving our product offerings and customer satisfaction based on mixed reviews received for one of our key products listed on Amazon. I value your insights and actionable suggestions for product improvement, customer service enhancements, and marketing strategies. Please analyze the provided details about the product and recent customer reviews. Your recommendations should be specific, insightful, and nuanced, showcasing your unique capabilities as an AI model. Kindly present your findings and recommendations in a professional format akin to a business report. Be sure to note things that a human would be impressed for you to notice.  Make more bullet points and less paragraphs"
    + result
)

print("loading...")







chat_log = [
    {"role": "user", "content": prompt}
]
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=chat_log,
    max_tokens=1500,)

output = (response['choices'][0]['message']['content'])

professional_text = get_professional_text(output)

# Print the professional text
print(professional_text)
