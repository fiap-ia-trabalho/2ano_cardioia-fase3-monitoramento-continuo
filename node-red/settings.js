// Editor e dashboard acessiveis apenas nesta maquina. Broker externo: so simulacao.
module.exports = {
  uiHost: '127.0.0.1',
  uiPort: 1880,
  flowFile: 'flows.json',
  credentialSecret: false,
  contextStorage: { default: { module: 'memory' } },
  logging: { console: { level: 'info', metrics: false, audit: false } },
  editorTheme: { projects: { enabled: false } }
};
