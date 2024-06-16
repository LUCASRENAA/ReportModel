from rest_framework import serializers

from .models import Report,SettingsReport


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = '__all__'


class SettingsReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = SettingsReport
        fields = '__all__'
