from odoo import models, fields, api
import requests

class Project(models.Model):
    _inherit = 'project.project'

    mattermost_channel_id = fields.Char()

    def create_project_channel(self):
        headers = {'Authorization': 'Bearer ' + self.env['ir.config_parameter'].sudo().get_param('mattermost_token')}
        data = {'name': self.name}
        r = requests.post(self.env['ir.config_parameter'].sudo().get_param('mattermost_url') + '/api/v4/channels', json=data, headers=headers)
        if r.status_code == 200:
            self.mattermost_channel_id = r.json()['id']
        else:
            print('Error creating Mattermost channel:', r.json())

    def archive_project_channel(self):
        headers = {'Authorization': 'Bearer ' + self.env['ir.config_parameter'].sudo().get_param('mattermost_token')}
        data = {'delete_at': 1}
        r = requests.put(self.env['ir.config_parameter'].sudo().get_param('mattermost_url') + '/api/v4/channels/' + self.mattermost_channel_id + '/patch', json=data, headers=headers)
        if r.status_code == 200:
            self.mattermost_channel_id = False
        else:
            print('Error archiving Mattermost channel:', r.json())

    def create_task_message(self, task_id):
        headers = {'Authorization': 'Bearer ' + self.env['ir.config_parameter'].sudo().get_param('mattermost_token')}
        task = self.env['project.task'].browse(task_id)
        data = {'channel_id': self.mattermost_channel_id, 'message': 'New task created: ' + task.name}
        r = requests.post(self.env['ir.config_parameter'].sudo().get_param('mattermost_url') + '/api/v4/posts', json=data, headers=headers)
        if r.status_code != 200:
            print('Error creating Mattermost message:', r.json())

class Task(models.Model):
    _inherit = 'project.task'

    @api.model
    def create(self, vals):
        task = super(Task, self).create(vals)
        task.project_id.create_task_message(task.id)
        return task

