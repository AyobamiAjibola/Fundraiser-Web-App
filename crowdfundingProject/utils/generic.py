from babel.numbers import format_currency
from decimal import Decimal

def currency_display(amount):
    """
    Format the amount as Nigerian Naira (NGN) currency.
    """
    return format_currency(amount, 'NGN', locale='en_NG')

def format_amount(amount, is_kobo=False):
    """
    Formats the amount as currency. If the amount is in kobo, converts to naira.
    """
    if amount is None:
        return currency_display(0)
    
    if is_kobo:
        # Convert kobo to naira
        converted_to_naira = amount / 100
        return currency_display(converted_to_naira)
    
    return currency_display(amount)

def calc_progress(amountRaised, amountNeeded):
    
    if amountRaised is None or amountNeeded == 0:
        return 0
    else:
        value = (amountRaised / amountNeeded) * 100
        return round(value)

def character_breaker(sentence, max_chars):
    """
    Break the sentence into a string with a maximum number of characters.
    """
    if not sentence:
        return ""
    
    return sentence[:max_chars]

def word_breaker(sentence, max_words):
    """
    Break the sentence into a string with a maximum number of words.
    """
    if not sentence:
        return ""
    
    words = sentence.split()
    return ' '.join(words[:max_words])

def cal_total_amt(campaigns):
    total_amount = Decimal(0)
    for campaign in campaigns:
        amount = campaign.amountRaised or Decimal(0)
        total_amount += amount
    return format_amount(total_amount)


