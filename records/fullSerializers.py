from rest_framework import serializers

from foods.models import Foods
from foods.serializers import FoodsSerializer
from phasesDay.models import PhasesDay
from phasesDay.serializers import PhasesDaySerializer
from records.models import Records
from users.models import User
from users.serializers import UserSerializer


class FullRecordSerializer(serializers.ModelSerializer):
    foods = FoodsSerializer(many=True, read_only=True)
    phasesDay = PhasesDaySerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Records
        fields = ('id',
                  'blood_glucose',
                  'carbohydrates',
                  'annotations',
                  'hc_rations',
                  'bolus',
                  'foods',
                  'phasesDay',
                  'user',
                  'created_date',)


class UpdateRecordSerializer(serializers.ModelSerializer):
    idFoods = serializers.PrimaryKeyRelatedField(queryset=Foods.objects.all(), many=True, write_only=True)
    idPhaseDay = serializers.PrimaryKeyRelatedField(queryset=PhasesDay.objects.all(), write_only=True)
    user = UserSerializer(read_only=True)
    foods = FoodsSerializer(many=True, read_only=True)
    phasesDay = PhasesDaySerializer(read_only=True)

    class Meta:
        model = Records
        fields = (
                  'blood_glucose',
                  'carbohydrates',
                  'annotations',
                  'hc_rations',
                  'bolus',
                  'idFoods',
                  'idPhaseDay',
                  'foods',
                  'user',
                  'phasesDay',
                  'created_date')

    def update(self, instance, validated_data):
        foods = validated_data.pop('idFoods')
        phases_day = validated_data.pop('idPhaseDay')
        user = instance.user

        instance.foods.set(foods)
        instance.blood_glucose = validated_data.get('blood_glucose', instance.blood_glucose)
        instance.carbohydrates = validated_data.get('carbohydrates', instance.carbohydrates)
        instance.annotations = validated_data.get('annotations', instance.annotations)
        instance.hc_rations = validated_data.get('hc_rations', instance.hc_rations)
        instance.bolus = validated_data.get('bolus', instance.bolus)
        instance.phasesDay = phases_day
        instance.save()

        return Records.objects.get(id=instance.id)


class CreateRecordSerializer(serializers.ModelSerializer):
    idFoods = serializers.PrimaryKeyRelatedField(queryset=Foods.objects.all(), many=True, write_only=True)
    idPhaseDay = serializers.PrimaryKeyRelatedField(queryset=PhasesDay.objects.all(), write_only=True)
    user = UserSerializer(read_only=True)
    foods = FoodsSerializer(many=True, read_only=True)
    phasesDay = PhasesDaySerializer(read_only=True)

    class Meta:
        model = Records
        fields = ('blood_glucose',
                  'carbohydrates',
                  'annotations',
                  'hc_rations',
                  'bolus',
                  'idFoods',
                  'idPhaseDay',
                  'foods',
                  'user',
                  'phasesDay',
                  'created_date')

    def create(self, validated_data):
        foods = validated_data.pop('idFoods')
        phases_day = validated_data.pop('idPhaseDay')

        current_user = self.context.get('request').user

        instance = Records.objects.create(
            user=current_user,
            phasesDay=phases_day,
            **validated_data)

        instance.foods.set(foods)
        return instance


class PatchRecordSerializer(serializers.ModelSerializer):
    idUser = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True)
    idFoods = serializers.PrimaryKeyRelatedField(queryset=Foods.objects.all(), many=True, write_only=True)
    idPhaseDay = serializers.PrimaryKeyRelatedField(queryset=PhasesDay.objects.all(), write_only=True)

    class Meta:
        model = Records
        fields = ('blood_glucose',
                  'carbohydrates',
                  'annotations',
                  'hc_rations',
                  'bolus',
                  'idUser',
                  'idFoods',
                  'idPhaseDay',
                  'created_date')
