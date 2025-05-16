import openai

client = openai.OpenAI(api_key="Insert OpenAI API key here")

def chat_with_gpt(recipe, products):
    prompt = f'''
    You are a strict assistant helping a user match a recipe to available products.

    Given the following list of products: {products}

    Your task is to return ONLY the indices (zero-based) of the products that are absolutely required, clearly usable, or directly relevant for preparing this: "{recipe}". This may be a meal, a dish, or a food item.

    VERY IMPORTANT:
    - Only select products that are clearly usable as ingredients in the recipe.
    - Do NOT include ingredients that might be "possibly related" — if it's unclear, leave it out.
    - If something is just a topping, a snack, or loosely associated, DO NOT include it.
    - For example, if the recipe is 'pizza', do NOT suggest items like 'grill sausages', 'chorizo', or anything unless they are very clearly used in the specific type of pizza.
    - If the product is a drink, snack, candy, or unrelated food, exclude it.
    - Be conservative in your selections. It’s better to return too few matches than too many.
    - Return a maximum of six items
    
    Output MUST be only a list of the indices, without any explanation or text.
    If no products are suitable to prepare the recipe given, then return an empty list.
    If the recipe does not make sense, or is not related in any way to cooking or food, return this: Not related to food
    '''
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()

def get_recipe(user_recipe, selected_products):
    prompt = f'''
    You previously analyzed a list of products and determined that these items: {selected_products} are suitable to prepare the following meal: "{user_recipe}".

    Now, briefly explain how these specific products could be used to make the dish. Keep the explanation short, friendly, and focused on how the ingredients come together.
    
    IMPORTANT:
    - Do NOT start your answer with "Certainly", "Of course", "Sure", or any similar phrase.
    - Just get straight to the point in a casual, helpful tone — like an app assistant or a friend explaining how the recipe could work.
    '''

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()

def smart_scan_gpt(scanned_items, discount_products):

    prompt = f'''
    You are a strict assistant helping a user combine what they have in their fridge to available products with discount from supermarkets.

    Given the following list of products by the user: {scanned_items}

    Your task is to return ONLY the indices (zero-based) of the products that can be clearly combined the following products with discount: {discount_products}
    VERY IMPORTANT:
    - Only select products that are clearly usable with the user's products.
    - Do NOT include ingredients that might be "possibly related" — if it's unclear, leave it out.
    - If something is just a topping, a snack, or loosely associated, DO NOT include it.
    - For example, if the user input is a 'pizza', do NOT suggest items like 'grill sausages', 'chorizo', or anything unless they are very clearly used in the specific type of pizza.
    - If the product is a drink, snack, candy, or unrelated food, exclude it.
    - Be conservative in your selections. It’s better to return too few matches than too many.
    - Return a maximum of six items
    
    Output MUST be only a list of the indices, without any explanation or text.
    If no products are suitable to prepare the recipe given, then return an empty list.
    '''
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()

def get_smart_recipe(scanned_items, selected_products):
    prompt = f'''
    You previously analyzed a list of products and determined that these items: {scanned_items}, scanned by the user, are suitable to combine with the following: "{selected_products}".

    Can you suggest 2–3 meal ideas I can prepare using a mix of these items?

    IMPORTANT:
    - Do NOT start your answer with "Certainly", "Of course", "Sure", or any similar phrase.
    '''

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()
