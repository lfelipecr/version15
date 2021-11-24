# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import poplib
from ssl import SSLError
from socket import gaierror, timeout
from imaplib import IMAP4, IMAP4_SSL
from poplib import POP3, POP3_SSL
from xmlrpc import client as xmlrpclib
import email

from datetime import datetime, date, timedelta

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
import pytz
tz = pytz.timezone('America/Costa_Rica')
_logger = logging.getLogger(__name__)
MAX_POP_MESSAGES = 50
#MAX_POP_MESSAGES = 50
MAIL_TIMEOUT = 60


lotes = 40

# Workaround for Python 2.7.8 bug https://bugs.python.org/issue23906
poplib._MAXLINE = 65536

class FetchmailServer(models.Model):
    """Incoming POP/IMAP mail server account"""

    _inherit = 'fetchmail.server'

    date_get = fields.Datetime('Fecha y hora')
    logs = fields.Text()

    def fetch_mail(self):
        """ WARNING: meant for cron usage only - will commit() after each email! """
        additionnal_context = {
            'fetchmail_cron_running': True
        }
        MailThread = self.env['mail.thread']
        mensaje = ''
        for server in self:
            _logger.info('start checking for new emails on %s server %s', server.server_type, server.name)
            additionnal_context['default_fetchmail_server_id'] = server.id
            count, failed = 0, 0
            imap_server = None
            pop_server = None
            if server.server_type == 'imap':
                try:
                    imap_server = server.connect()
                    imap_server.select()
                    result, data = imap_server.search(None, '(UNSEEN)')

                    # nw = []
                    # for num in data[0].split():
                    #     nw.append(num)
                    #
                    # if len(nw) > MAX_POP_MESSAGES:
                    #     """APLICAMOS PROCESAMIENTO POR LOTES"""
                    #     imap_server = self._proccess_lots(MailThread, server, imap_server, len(nw), additionnal_context, 'imap')
                    # else:
                    for num in data[0].split():
                        res_id = None
                        result, data = imap_server.fetch(num, '(RFC822)')
                        imap_server.store(num, '-FLAGS', '\\Seen')
                        try:
                            if self._mapped_date(data[0][1], MailThread, server):
                                res_id = MailThread.with_context(**additionnal_context).message_process(server.object_id.model, data[0][1], save_original=server.original, strip_attachments=(not server.attach))
                        except Exception:
                            _logger.info('Failed to process mail from %s server %s.', server.server_type, server.name, exc_info=True)
                            failed += 1
                        imap_server.store(num, '+FLAGS', '\\Seen')
                        self._cr.commit()
                        count += 1
                    _logger.info("Fetched %d email(s) on %s server %s; %d succeeded, %d failed.", count, server.server_type, server.name, (count - failed), failed)
                except Exception:
                    _logger.info("General failure when trying to fetch mail from %s server %s.", server.server_type, server.name, exc_info=True)
                finally:
                    if imap_server:
                        imap_server.close()
                        imap_server.logout()
            elif server.server_type == 'pop':
                try:
                    while True:
                        pop_server = server.connect()
                        (num_messages, total_size) = pop_server.stat()
                        pop_server.list()
                        if num_messages > MAX_POP_MESSAGES:
                           """APLICAMOS PROCESAMIENTO POR LOTES"""
                           pop_server = self._proccess_lots(MailThread, server, pop_server, num_messages, additionnal_context, 'pop')
                        else:
                            mensaje = ''
                            mensaje += 'Fecha y hora : ' + datetime.now().isoformat() + ' >> Conexión normal al servidor ' + str('\n')
                            mensaje += 'Fecha y hora : ' + datetime.now().isoformat() + ' >> Total a Procesar %s ' % (num_messages) + str('\n')
                            not_process = 0
                            for num in range(1, min(MAX_POP_MESSAGES, num_messages) + 1):
                                (header, messages, octets) = pop_server.retr(num)
                                message = (b'\n').join(messages)
                                res_id = None
                                try:
                                    if self._mapped_date(message, MailThread, server):
                                        res_id = MailThread.with_context(**additionnal_context).message_process(server.object_id.model, message, save_original=server.original, strip_attachments=(not server.attach))
                                    else:
                                        not_process += 1
                                    pop_server.dele(num)
                                except Exception:
                                    _logger.info('Failed to process mail from %s server %s.', server.server_type, server.name, exc_info=True)
                                    failed += 1
                                self.env.cr.commit()

                            mensaje += 'Fecha y hora : ' + datetime.now().isoformat() + ' >> Procesados : %s ' % (num_messages - not_process) + str('\n')
                            mensaje += 'Fecha y hora : ' + datetime.now().isoformat() + ' >> No entran a Procesar : %s ' % (not_process) + str('\n')
                            if num_messages < MAX_POP_MESSAGES:
                                break
                            pop_server.quit()
                            mensaje += 'Fecha y hora : ' + datetime.now().isoformat() + ' >> Cerrando conexión ' + str('\n')
                            _logger.info("Fetched %d email(s) on %s server %s; %d succeeded, %d failed.", num_messages, server.server_type, server.name, (num_messages - failed), failed)
                except Exception:
                    _logger.info("General failure when trying to fetch mail from %s server %s.", server.server_type, server.name, exc_info=True)
                finally:
                    if pop_server:
                        pop_server.quit()
                        mensaje += 'Fecha y hora : ' + datetime.now().isoformat() + ' >> Cerrando conexión ' + str('\n')

            if server:
                if not server.logs:
                    server.logs = ''
            server.logs = mensaje
            server.write({'date': fields.Datetime.now()})
        return True


    def _mapped_date(self, message,MailThread,server):
        if isinstance(message, xmlrpclib.Binary):
            message = bytes(message.data)
        if isinstance(message, str):
            message = message.encode('utf-8')
        message = email.message_from_bytes(message, policy=email.policy.SMTP)
        # parse the message, verify we are not in a loop by checking message_id is not duplicated
        msg_dict = MailThread.message_parse(message, save_original=False)
        #Mio
        if msg_dict['email_from']:
            if server.date_get:
                #Nota: Mapea los correos que son a partir de la fecha dada en el servidor de correos
                date_server = tz.normalize(tz.localize(server.date_get) - timedelta(hours=5))
                if 'date' in msg_dict:
                    if msg_dict['date'] != False or msg_dict['date'] is not None:
                        date_mail_utc = datetime.strptime(msg_dict['date'],'%Y-%m-%d %H:%M:%S')
                        date_mail = tz.normalize(tz.localize(date_mail_utc) - timedelta(hours=6))
                        if not date_server <= date_mail:
                            return False
        return True

    #Algoritmo
    def _proccess_lots(self,MailThread , server, mail_server, num_messages, additionnal_context, type):
        mensaje = ''
        failed = 0
        mensaje += 'Fecha y hora : ' + datetime.now().isoformat() + ' >> Total de mensajes a procesar %s ' % (num_messages)  + str('\n')
        def _separator_lots(total, lotes):
            div = total / lotes
            part = int(div) + 1 if div > int(div) else int(div)
            return part

        lots = _separator_lots(num_messages, lotes)
        mensaje += 'Fecha y hora : ' + datetime.now().isoformat() + ' >> Se procesarán en %s lotes' % (lots)  + str('\n')
        array_lot = []
        total = num_messages
        for x in range(1, lots + 1):
            r = total - lotes
            if r > 0:
                array_lot.append({'lote': x, 'limit': lotes})
            else:
                array_lot.append({'lote': x, 'limit': total})
            total = r
        if type == 'pop':
            mensaje += self._lots_pop(array_lot, mail_server, server, mensaje, additionnal_context, MailThread)
        else:
            raise UserError(_('SOLO FUNCIONARÁ PARA POP'))
            #mensaje += self._lots_imap(array_lot, mail_server, server, mensaje, additionnal_context, MailThread)
        if not server.logs:
            server.logs = ''
        server.logs += mensaje
        return False


    def _lots_pop(self, array_lot, mail_server, server, mensaje, additionnal_context, MailThread):

        mail_server.quit()
        mensaje += mensaje


        for i in array_lot:
            mensaje += 'Fecha y hora : ' + datetime.now().isoformat() + ' >> Conexión N° %s al servidor ' % (i['lote']) + str('\n')
            pop_server1 = server.connect()
            (num_messages, total_size) = pop_server1.stat()
            pop_server1.list()
            mensaje += 'Fecha y hora : ' + datetime.now().isoformat() + ' >> Cantidad de mensajes a procesar: %s ' % (i['limit']) + str('\n')

            count, failed = 0, 0
            not_process = 0
            for num in range(1, i['limit'] + 1):
                (header, messages, octets) = pop_server1.retr(num)
                message = (b'\n').join(messages)
                res_id = None
                try:
                    if self._mapped_date(message, MailThread, server):
                        res_id = MailThread.with_context(**additionnal_context).message_process(server.object_id.model, message, save_original=server.original, strip_attachments=(not server.attach))
                    else:
                        not_process += 1
                    pop_server1.dele(num)
                except Exception:
                    _logger.info('Failed to process mail from %s server %s.', server.server_type, server.name, exc_info=True)
                    failed += 1
                self.env.cr.commit()

            mensaje += 'Fecha y hora : ' + datetime.now().isoformat() + ' >> Correctos : %s ' % (i['limit'] - not_process) + str('\n')
            mensaje += 'Fecha y hora : ' + datetime.now().isoformat() + ' >> No entran a procesar : %s ' % (not_process) + str('\n')

            pop_server1.quit()
            mensaje += 'Fecha y hora : ' + datetime.now().isoformat() + ' >> Cerrando conexión N° %s ' % (i['lote']) + str('\n')

        return mensaje

    #
    # def _lots_imap(self, array_lot, mail_server, server, mensaje, additionnal_context, MailThread):
    #
    #     mail_server.close()
    #     mail_server.logout()
    #
    #     mensaje += mensaje
    #     not_process = 0
    #     count, failed = 0, 0
    #
    #     init = 0
    #     for i in array_lot:
    #         mensaje += 'Fecha y hora : ' + datetime.now().isoformat() + ' >> Conexión N° %s al servidor ' % (i['lote']) + str('\n')
    #         imap_server1 = server.connect()
    #         imap_server1.select()
    #         result, data = imap_server1.search(None, '(UNSEEN)')
    #         mensaje += 'Fecha y hora : ' + datetime.now().isoformat() + ' >> Cantidad de mensajes a procesar: %s ' % (i['limit']) + str('\n')
    #
    #         #for num in data[0].split():
    #         nw = []
    #         for num in data[0].split():
    #             nw.append(num)
    #
    #         #HASTA AQUÍ ME QUEDÉ, SEGÚN FELIPE, SOLO FUNCIONARÁ CON POP
    #
    #         for num in nw[init:i['limit']]:
    #             res_id = None
    #             result, data = imap_server1.fetch(num, '(RFC822)')
    #             imap_server1.store(num, '-FLAGS', '\\Seen')
    #             try:
    #                 res_id = MailThread.with_context(**additionnal_context).message_process(server.object_id.model, data[0][1], save_original=server.original, strip_attachments=(not server.attach))
    #             except Exception:
    #                 _logger.info('Failed to process mail from %s server %s.', server.server_type, server.name, exc_info=True)
    #                 failed += 1
    #             imap_server1.store(num, '+FLAGS', '\\Seen')
    #             self._cr.commit()
    #             count += 1
    #
    #         init = i['limit']
    #
    #         mensaje += 'Fecha y hora : ' + datetime.now().isoformat() + ' >> Correctos : %s ' % (i['limit'] - not_process) + str('\n')
    #         mensaje += 'Fecha y hora : ' + datetime.now().isoformat() + ' >> No entran a procesar : %s ' % (not_process) + str('\n')
    #
    #         imap_server1.close()
    #         imap_server1.logout()
    #
    #         mensaje += 'Fecha y hora : ' + datetime.now().isoformat() + ' >> Cerrando conexión N° %s ' % (i['lote']) + str('\n')
    #
    #     return mensaje
    #
    #
    #

