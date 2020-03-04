#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from webapp import create_app
from webapp.modules import config
from webapp.modules import port

if __name__ == "__main__":
    app = create_app()
    app.run(host=config['host'], port=port)
