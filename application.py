from flask import Flask
from flask_ask import Ask, statement, question, request, session, version

def create(continente, logger, schema):
    app = Flask(__name__)
    ask = Ask(app, '/continente')

    @ask.launch
    def launch():
        logger.debug('launch')
        continente.loggerin_async()
        return question('What would you like to do?') \
                .reprompt("I didn't get that. What can I do for you?")

    @ask.on_session_started
    def new_session():
        logger.debug('session started')

    @ask.session_ended
    def session_end():
        logger.debug('session ended')
        return statement('Something went wrong')
            
    @ask.intent('AMAZON.StopIntent')
    def stop():
        logger.debug('stop')
        return statement('Ok')
            
    @ask.intent('AMAZON.CancelIntent')
    def stop():
        logger.debug('cancel')
        return statement('Ok')
            
    @ask.intent('AMAZON.HelpIntent')
    def help():
        logger.debug('help')
        intro = 'Try something like "add coke" or "give me the summary".'
        message = intro + ' Check your alexa app for a full list of supported products. What do you wish to do?'

        card_content = intro + "\nSupported products include:\n" + "\n".join(continente.products.values())

        return question(message) \
                .simple_card(
                    title= 'Things to try',
                    content= card_content
                )

    @ask.intent('Add', mapping= {'name': 'Product'})
    def add(name):
        logger.debug('add')
        resolutions = request['intent']['slots']['Product'].get('resolutions', {}).get('resolutionsPerAuthority', [])
        logger.warn(resolutions)
        #todo: use resolutions
        product = continente.search(name)
        if product is None:
            return question('{} not found. Anything else?'.format(name))
        product = continente.add(product)

        return question('{} added. Anything else?'.format(name)) \
                .standard_card(title= product.title,
                               text= unicode("{}\n{}\n{}").format(product.brand, product.notes, product.unit_price),
                               small_image_url= product.small_image,
                               large_image_url= product.large_image)

    @ask.intent('Summary')
    def summary():
        logger.debug('summary')
        summary = continente.summary()
        return statement('{} items with a total of {} euro'.format(summary.quantity, summary.price))

    return app
