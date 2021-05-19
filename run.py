from app import create_app
from scheduler import scheduler
import sys

# app = create_app('config.DevelopmentConfig')
app = create_app('config.ProductionConfig')
# if __name__ == '__main__':
#     app = create_app('config.DevelopmentConfig')

#     if len(sys.argv) > 1:
#         if sys.argv[1] == 'prod':
#             app = create_app('config.ProductionConfig')

#     scheduler.init_app(app)
#     scheduler.start()
#     app.run()

# app = create_app('config.DevelopmentConfig')

# if len(sys.argv) > 1:
#     if sys.argv[1] == 'prod':
#         app = create_app('config.ProductionConfig')

# scheduler.init_app(app)
# scheduler.start()
# app.run()
