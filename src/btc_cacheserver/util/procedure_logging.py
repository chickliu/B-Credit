#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
created by antimoth at 2017-12-08
"""

import inspect
import logging

class ProcedureDefine(object):
    pass


class ProcedureBase(object):

    def current(self):
        return self._procedure + self._target

    def stack(self):
        return self._stack or [self.current(), ]

    def procedure(self):
        _stack_procedure = getattr(self, "_stack_procedure", None)
        if _stack_procedure is None:
            _stack_procedure = " <= ".join(self.stack())
            setattr(self, "_stack_procedure", _stack_procedure)
        return _stack_procedure

    def start(self, request, *args, **kwargs):
        msg = self.format_log_info("INFO", request, proc="started")
        self.logger.info(msg, *args, **kwargs)

    def end(self, response, *args, **kwargs):
        msg = self.format_log_info("INFO", response, proc="ended")
        self.logger.info(msg, *args, **kwargs)


class Procedure(ProcedureBase):

    logger = logging.getLogger("procedure")

    def __init__(self, s_target, s_procedure=None):

        stacks = inspect.stack()

        if s_procedure is None:
            s_procedure = stacks[1][3]  # in which method called this __init__
        self._procedure = s_procedure

        if not isinstance(s_target, str):
            s_target = repr(s_target)
        self._target = s_target
        
        self._stack = []

        for stack in stacks: 
            _iframe = stack[0]

            for obj in _iframe.f_locals.values():
                if not isinstance(obj, Procedure):
                    continue

                self._stack.extend(obj.stack())

            if len(self._stack) > 1:
                break

    def format_log_info(self, level, msg, proc="processing"):
        current_call = inspect.stack()[2]
        _iframe = current_call[0]
        line_no = _iframe.f_lineno
        module_name = _iframe.f_globals.get("__name__", "")
        method_name = current_call[3]
        class_name = _iframe.f_locals.get('self', None).__class__.__name__
        ex_msg = "[{filename}:{class_name}:{lineno}] [{method}] [{level}] - ".format(
                filename=module_name, class_name=class_name, lineno=line_no, method=method_name, level=level)
        return "{extra_msg}{pd_ins}, {curproc} >>> {msg_tmp}".format(extra_msg=ex_msg, pd_ins=repr(self), curproc=proc, msg_tmp=msg)

    def info(self, msg, *args, **kwargs):
        msg = self.format_log_info("INFO", msg)
        self.logger.info(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        msg = self.format_log_info("ERROR", msg)
        self.logger.error(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        msg = self.format_log_info("DEBUG", msg)
        self.logger.debug(msg, *args, **kwargs)

    def warn(self, msg, *args, **kwargs):
        msg = self.format_log_info("WARNING", msg)
        self.logger.warning(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        msg = self.format_log_info("CRITICAL", msg)
        self.logger.critical(msg, *args, **kwargs)

    def exception(self, msg, *args, **kwargs):
        msg = self.format_log_info("ERROR", msg)
        kwargs["exc_info"] = 1
        self.logger.error(msg, *args, **kwargs)

    def __repr__(self):
        return "Procedure( {pcd_ins} )".format(pcd_ins=self.procedure())

    __str__ = __repr__


if __name__ == "__main__":
    import sys
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    def funca():
        p = Procedure("<a>")
        p.info("test : %s", "a")
    
    
    def funcb():
        p = Procedure("<b>")
        funca()
        p.warn("test : %s", "b")
    
    
    def funcc():
        p = Procedure("<c>")
        funcb()
        p.error("test : %s", "c")

    funcc()
    funcb()


