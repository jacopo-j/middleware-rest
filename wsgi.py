#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from webapp import app
import os

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000))
