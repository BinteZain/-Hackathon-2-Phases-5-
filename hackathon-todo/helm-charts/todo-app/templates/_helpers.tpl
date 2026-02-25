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
{{- if .Values.global.extraLabels }}
{{ toYaml .Values.global.extraLabels }}
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
Frontend fullname
*/}}
{{- define "todo-app.frontend.fullname" -}}
{{- printf "%s-%s" (include "todo-app.fullname" .) .Values.frontend.name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Backend fullname
*/}}
{{- define "todo-app.backend.fullname" -}}
{{- printf "%s-%s" (include "todo-app.fullname" .) .Values.backend.name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Frontend image name
*/}}
{{- define "todo-app.frontend.image" -}}
{{- $registry := .Values.global.imageRegistry }}
{{- $repo := .Values.frontend.image.repository }}
{{- $tag := .Values.frontend.image.tag | default .Chart.AppVersion }}
{{- if $registry }}
{{- printf "%s/%s:%s" $registry $repo $tag }}
{{- else }}
{{- printf "%s:%s" $repo $tag }}
{{- end }}
{{- end }}

{{/*
Backend image name
*/}}
{{- define "todo-app.backend.image" -}}
{{- $registry := .Values.global.imageRegistry }}
{{- $repo := .Values.backend.image.repository }}
{{- $tag := .Values.backend.image.tag | default .Chart.AppVersion }}
{{- if $registry }}
{{- printf "%s/%s:%s" $registry $repo $tag }}
{{- else }}
{{- printf "%s:%s" $repo $tag }}
{{- end }}
{{- end }}

{{/*
Create image pull secrets
*/}}
{{- define "todo-app.imagePullSecrets" -}}
{{- if .Values.global.imagePullSecrets }}
imagePullSecrets:
{{ toYaml .Values.global.imagePullSecrets | indent 2 }}
{{- end }}
{{- end }}

{{/*
Return the appropriate apiVersion for deployment.
*/}}
{{- define "todo-app.deployment.apiVersion" -}}
{{- if semverCompare "<1.14-0" .Capabilities.KubeVersion.GitVersion -}}
{{- print "extensions/v1beta1" -}}
{{- else if semverCompare "<1.16-0" .Capabilities.KubeVersion.GitVersion -}}
{{- print "apps/v1beta2" -}}
{{- else -}}
{{- print "apps/v1" -}}
{{- end }}
{{- end }}

{{/*
Return the appropriate apiVersion for HPA.
*/}}
{{- define "todo-app.hpa.apiVersion" -}}
{{- if semverCompare "<1.23-0" .Capabilities.KubeVersion.GitVersion -}}
{{- print "autoscaling/v2beta1" -}}
{{- else -}}
{{- print "autoscaling/v2" -}}
{{- end }}
{{- end }}

{{/*
Return the appropriate apiVersion for ingress.
*/}}
{{- define "todo-app.ingress.apiVersion" -}}
{{- if semverCompare "<1.14-0" .Capabilities.KubeVersion.GitVersion -}}
{{- print "extensions/v1beta1" -}}
{{- else if semverCompare "<1.19-0" .Capabilities.KubeVersion.GitVersion -}}
{{- print "networking.k8s.io/v1beta1" -}}
{{- else -}}
{{- print "networking.k8s.io/v1" -}}
{{- end }}
{{- end }}

{{/*
Return the appropriate apiVersion for PDB.
*/}}
{{- define "todo-app.pdb.apiVersion" -}}
{{- if semverCompare "<1.21-0" .Capabilities.KubeVersion.GitVersion -}}
{{- print "policy/v1beta1" -}}
{{- else -}}
{{- print "policy/v1" -}}
{{- end }}
{{- end }}

{{/*
Return the appropriate apiVersion for network policy.
*/}}
{{- define "todo-app.networkPolicy.apiVersion" -}}
{{- if semverCompare "<1.19-0" .Capabilities.KubeVersion.GitVersion -}}
{{- print "networking.k8s.io/v1beta1" -}}
{{- else -}}
{{- print "networking.k8s.io/v1" -}}
{{- end }}
{{- end }}

{{/*
Generate certificates for HTTPS
*/}}
{{- define "todo-app.generateSecret" -}}
{{- $secret := lookup "v1" "Secret" .namespace .name -}}
{{- if $secret -}}
{{- index $secret.data .key -}}
{{- else -}}
{{- (randAlphaNum 32) | b64enc -}}
{{- end -}}
{{- end -}}
