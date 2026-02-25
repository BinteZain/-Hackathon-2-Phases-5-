{{/*
Expand the name of the chart.
*/}}
{{- define "todo-app.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "todo-app.fullname" -}}
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
{{- define "todo-app.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "todo-app.labels" -}}
helm.sh/chart: {{ include "todo-app.chart" . }}
{{ include "todo-app.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- if .Values.global.commonLabels }}
{{ toYaml .Values.global.commonLabels }}
{{- end }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "todo-app.selectorLabels" -}}
app.kubernetes.io/name: {{ include "todo-app.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Frontend labels
*/}}
{{- define "todo-app.frontend.labels" -}}
{{ include "todo-app.labels" . }}
app.kubernetes.io/component: frontend
app.kubernetes.io/instance: {{ .Release.Name }}-frontend
{{- end }}

{{/*
Frontend selector labels
*/}}
{{- define "todo-app.frontend.selectorLabels" -}}
{{ include "todo-app.selectorLabels" . }}
app.kubernetes.io/component: frontend
{{- end }}

{{/*
Backend labels
*/}}
{{- define "todo-app.backend.labels" -}}
{{ include "todo-app.labels" . }}
app.kubernetes.io/component: backend
app.kubernetes.io/instance: {{ .Release.Name }}-backend
{{- end }}

{{/*
Backend selector labels
*/}}
{{- define "todo-app.backend.selectorLabels" -}}
{{ include "todo-app.selectorLabels" . }}
app.kubernetes.io/component: backend
{{- end }}

{{/*
PostgreSQL labels
*/}}
{{- define "todo-app.postgresql.labels" -}}
{{ include "todo-app.labels" . }}
app.kubernetes.io/component: postgresql
app.kubernetes.io/instance: {{ .Release.Name }}-postgres
{{- end }}

{{/*
PostgreSQL selector labels
*/}}
{{- define "todo-app.postgresql.selectorLabels" -}}
{{ include "todo-app.selectorLabels" . }}
app.kubernetes.io/component: postgresql
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "todo-app.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "todo-app.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the frontend service account
*/}}
{{- define "todo-app.frontend.serviceAccountName" -}}
{{- if .Values.frontend.serviceAccount.create }}
{{- default "frontend-sa" .Values.frontend.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.frontend.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the backend service account
*/}}
{{- define "todo-app.backend.serviceAccountName" -}}
{{- if .Values.backend.serviceAccount.create }}
{{- default "backend-sa" .Values.backend.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.backend.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the postgresql service account
*/}}
{{- define "todo-app.postgresql.serviceAccountName" -}}
{{- if .Values.postgresql.serviceAccount.create }}
{{- default "postgres-sa" .Values.postgresql.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.postgresql.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create a fully qualified name for frontend
*/}}
{{- define "todo-app.frontend.fullname" -}}
{{- printf "%s-frontend" (include "todo-app.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a fully qualified name for backend
*/}}
{{- define "todo-app.backend.fullname" -}}
{{- printf "%s-backend" (include "todo-app.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a fully qualified name for postgresql
*/}}
{{- define "todo-app.postgresql.fullname" -}}
{{- printf "%s-postgres" (include "todo-app.fullname" .) | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create the namespace name
*/}}
{{- define "todo-app.namespace" -}}
{{- default .Values.global.namespace .Release.Namespace }}
{{- end }}

{{/*
Get the image pull secrets
*/}}
{{- define "todo-app.imagePullSecrets" -}}
{{- if .Values.global.imagePullSecrets }}
imagePullSecrets:
{{- range .Values.global.imagePullSecrets }}
  - name: {{ . }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Get the image repository with optional global registry
Usage: include "todo-app.imageRepository" (dict "image" .Values.frontend.image "context" $)
*/}}
{{- define "todo-app.imageRepository" -}}
{{- $image := .image -}}
{{- $ctx := .context -}}
{{- if and $ctx.Values.global $ctx.Values.global.imageRegistry }}
{{- printf "%s/%s" $ctx.Values.global.imageRegistry $image.repository }}
{{- else }}
{{- $image.repository }}
{{- end }}
{{- end }}

{{/*
Get the database URL from secret or config
*/}}
{{- define "todo-app.databaseUrl" -}}
{{- $passwordSecret := .Values.postgresql.passwordSecret }}
{{- printf "postgresql://%s:$(POSTGRES_PASSWORD)@%s:5432/%s" .Values.postgresql.env.POSTGRES_USER (include "todo-app.postgresql.fullname" .) .Values.postgresql.env.POSTGRES_DB }}
{{- end }}
