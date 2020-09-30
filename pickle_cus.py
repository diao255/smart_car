#!/usr/bin/env python
# -*-coding:utf-8 -*-

import pickle


def load(path):
    model = None
    with open(path, 'rb')as r:
        data = r.read()
        model = pickle.loads(data)
    return model


def dump(model, path):
    with open(path, 'wb')as w:
        data = pickle.dumps(model)
        w.write(data)
