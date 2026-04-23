{{- define "req2veri.name" -}}
req2veri
{{- end }}

{{- define "req2veri.labels" -}}
app.kubernetes.io/name: {{ include "req2veri.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
