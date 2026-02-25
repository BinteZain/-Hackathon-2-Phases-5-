{{/*
Expand the name of the chart.
*/}}
{{- define "phase3.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "phase3.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "phase3.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "phase3.labels" -}}
helm.sh/chart: {{ include "phase3.chart" . }}
{{ include "phase3.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "phase3.selectorLabels" -}}
app.kubernetes.io/name: {{ include "phase3.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "phase3.serviceAccountName" -}}
{{- if .Values.rbac.serviceAccount.create }}
{{- default (include "phase3.fullname" .) .Values.rbac.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.rbac.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Frontend labels
*/}}
{{- define "phase3.frontend.labels" -}}
{{ include "phase3.labels" . }}
app.kubernetes.io/component: frontend
{{- end }}

{{/*
Frontend selector labels
*/}}
{{- define "phase3.frontend.selectorLabels" -}}
{{ include "phase3.selectorLabels" . }}
app.kubernetes.io/component: frontend
{{- end }}

{{/*
Backend labels
*/}}
{{- define "phase3.backend.labels" -}}
{{ include "phase3.labels" . }}
app.kubernetes.io/component: backend
{{- end }}

{{/*
Backend selector labels
*/}}
{{- define "phase3.backend.selectorLabels" -}}
{{ include "phase3.selectorLabels" . }}
app.kubernetes.io/component: backend
{{- end }}

{{/*
PostgreSQL labels
*/}}
{{- define "phase3.postgresql.labels" -}}
{{ include "phase3.labels" . }}
app.kubernetes.io/component: postgresql
{{- end }}

{{/*
PostgreSQL selector labels
*/}}
{{- define "phase3.postgresql.selectorLabels" -}}
{{ include "phase3.selectorLabels" . }}
app.kubernetes.io/component: postgresql
{{- end }}

{{/*
Generate the database URL
*/}}
{{- define "phase3.databaseUrl" -}}
{{- $user := .Values.secrets.postgresUser -}}
{{- $password := .Values.secrets.postgresPassword -}}
{{- $db := .Values.secrets.postgresDB -}}
{{- printf "postgresql://%s:%s@%s-postgresql:%d/%s?sslmode=disable" $user $password (include "phase3.fullname" .) 5432 $db -}}
{{- end }}

{{/*
Generate secrets
*/}}
{{- define "phase3.generatePassword" -}}
{{- if .Values.secrets.postgresPassword }}
{{- .Values.secrets.postgresPassword }}
{{- else }}
{{- randAlphaNum 32 }}
{{- end }}
{{- end }}

{{- define "phase3.generateAuthSecret" -}}
{{- if .Values.secrets.betterAuthSecret }}
{{- .Values.secrets.betterAuthSecret }}
{{- else }}
{{- randAlphaNum 32 }}
{{- end }}
{{- end }}
