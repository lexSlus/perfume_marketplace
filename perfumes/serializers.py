from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from accounts.serializers import AccountSerializer, AccountSerializerWithToken
from perfumes.models import Perfume, Review, Brand, Category, Offer, ReviewReply


class ReviewReplySerializer(serializers.ModelSerializer):
    user = AccountSerializer(read_only=True)
    review = serializers.PrimaryKeyRelatedField(queryset=Review.objects.all(), write_only=True)

    class Meta:
        model = ReviewReply
        fields = ['id', 'user', 'comment', 'created_at', 'review']

    def create(self, validated_data):
        user = self.context['request'].user
        return ReviewReply.objects.create(user=user, **validated_data)


class ReviewSerializer(serializers.ModelSerializer):
    user = AccountSerializer(read_only=True)
    replies = ReviewReplySerializer(many=True, read_only=True)

    class Meta:
        model = Review
        fields = '__all__'

    def create(self, validated_data):
        user = self.context['request'].user
        return Review.objects.create(user=user, **validated_data)


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class PerfumeSerializer(serializers.ModelSerializer):
    user = AccountSerializerWithToken(read_only=True)
    brand = BrandSerializer()
    category = CategorySerializer()
    reviews = ReviewSerializer(many=True, read_only=True)
    price = SerializerMethodField()

    class Meta:
        model = Perfume
        fields = '__all__'

    def get_price(self, obj):
        return obj.get_price_range()


class OfferSerializer(serializers.ModelSerializer):
    brand = serializers.PrimaryKeyRelatedField(queryset=Brand.objects.all())
    perfume = serializers.PrimaryKeyRelatedField(queryset=Perfume.objects.all())
    perfume_data = PerfumeSerializer(source='perfume', read_only=True)

    class Meta:
        model = Offer
        fields = ['id', 'image1', 'image2', 'description', 'quantity', 'price_per_ml', 'seller', 'perfume', 'brand',
                  'category', 'perfume_data']
        read_only_fields = ['seller', 'category']

    def create(self, validated_data):
        perfume = validated_data.get('perfume')
        offer = Offer.objects.create(**validated_data, category=perfume.category)
        return offer

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['category'] = instance.category.id if instance.category else None
        return representation
