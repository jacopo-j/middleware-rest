#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from webapp import create_app

if __name__ == "__main__":
    app = create_app()
    app.run(host='0.0.0.0', port=5000)
