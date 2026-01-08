from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .forms import FoodForm, ElectricityForm, TravelForm, WasteForm
from .utils import (
    calculate_food_carbon,
    calculate_electricity_carbon,
    calculate_travel_carbon,
    calculate_waste_carbon
)
from .models import (
    FoodConsumption,
    ElectricityUsage,
    Travel,
    WasteSegregation,
    FoodEmissionFactor
)

import json
import requests
import base64


# ================== CARBON SUMMARY ==================
@login_required
def carbon_summary(request):
    food_data = FoodConsumption.objects.filter(user=request.user)
    electricity_data = ElectricityUsage.objects.filter(user=request.user)
    travel_data = Travel.objects.filter(user=request.user)
    waste_data = WasteSegregation.objects.filter(user=request.user)

    food_total = sum(item.carbon_kg for item in food_data)
    electricity_total = sum(item.carbon_kg for item in electricity_data)
    travel_total = sum(item.carbon_kg for item in travel_data)
    waste_total = sum(item.carbon_kg for item in waste_data)

    overall_total = (
        food_total
        + electricity_total
        + travel_total
        + waste_total
    )

    context = {
        "food_data": food_data,
        "electricity_data": electricity_data,
        "travel_data": travel_data,
        "waste_data": waste_data,
        "food_total": food_total,
        "electricity_total": electricity_total,
        "travel_total": travel_total,
        "waste_total": waste_total,
        "overall_total": overall_total,
    }

    return render(request, "carbon_summary.html", context)


# ================== IMAGE ANALYSIS ==================
@login_required
def scan_waste(request):
    if request.method == "GET":
        return render(request, "scan_waste.html")

    if request.method == "POST":
        image = request.FILES.get("image")

        if not image:
            return JsonResponse({"error": "No image uploaded"}, status=400)

        # Convert image to base64 (for vision models later)
        image_bytes = image.read()
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

        # MOCK AI RESPONSE (temporary)
        detected_material = "Plastic"
        estimated_weight = 1.2  # kg
        emission_factor = 6.0   # kg CO₂ per kg plastic
        carbon_emission = estimated_weight * emission_factor

        return JsonResponse({
            "material": detected_material,
            "estimated_weight": estimated_weight,
            "carbon_emission": carbon_emission,
            "note": "Values are AI-estimated"
        })


# ================== DASHBOARD ==================
@login_required
def dashboard(request):
    return render(request, "dashboard.html")


# ================== FOOD ==================
@login_required
def food(request):
    if request.method == "POST":
        form = FoodForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user

            obj.carbon_kg = calculate_food_carbon(
                obj.quantity_kg,
                obj.food.emission_factor
            )

            obj.save()
            return redirect("dashboard")
    else:
        form = FoodForm()

    food_factors = FoodEmissionFactor.objects.all()

    return render(
        request,
        "food.html",
        {
            "form": form,
            "food_factors": food_factors
        }
    )


# ================== ELECTRICITY ==================
@login_required
def electricity(request):
    if request.method == "POST":
        form = ElectricityForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.carbon_kg = calculate_electricity_carbon(obj.units_kwh)
            obj.save()
            return redirect("dashboard")
    else:
        form = ElectricityForm()

    return render(request, "electricity.html", {"form": form})


# ================== TRAVEL ==================
@login_required
def travel(request):
    if request.method == "POST":
        form = TravelForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.carbon_kg = calculate_travel_carbon(
                obj.distance_km,
                obj.mode
            )
            obj.save()
            return redirect("dashboard")
    else:
        form = TravelForm()

    return render(request, "travel.html", {"form": form})


# ================== WASTE ==================
@login_required
def waste(request):
    if request.method == "POST":
        form = WasteForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.carbon_kg = calculate_waste_carbon(obj.quantity_kg)
            obj.save()
            return redirect("dashboard")
    else:
        form = WasteForm()

    return render(request, "waste.html", {"form": form})


# ================== CARBON ADVISOR ==================
@login_required
def carbon_advisor(request):
    return render(request, "carbon_advisor.html")


@csrf_exempt
@login_required
def carbon_advisor_chat(request):
    if request.method != "POST":
        return JsonResponse({"reply": "Invalid request"}, status=400)

    try:
        data = json.loads(request.body)
        user_message = data.get("message", "")

        food = sum(i.carbon_kg for i in FoodConsumption.objects.filter(user=request.user))
        electricity = sum(i.carbon_kg for i in ElectricityUsage.objects.filter(user=request.user))
        travel = sum(i.carbon_kg for i in Travel.objects.filter(user=request.user))
        waste = sum(i.carbon_kg for i in WasteSegregation.objects.filter(user=request.user))

        prompt = f"""
You are a sustainability advisor.

User carbon emissions (kg CO₂):
Food: {food}
Electricity: {electricity}
Travel: {travel}
Waste: {waste}

User question:
{user_message}

Give clear, practical, personalized advice.
"""

        headers = {
            "Authorization": "Bearer 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",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "ZeroCarbon App"
        }

        payload = {
            "model": "openai/gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are a helpful sustainability advisor."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.5
        }

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )

        response.raise_for_status()

        result = response.json()
        reply = result["choices"][0]["message"]["content"]

        return JsonResponse({"reply": reply})

    except Exception as e:
        print("SERVER ERROR:", repr(e))
        return JsonResponse({"reply": "Server error occurred."}, status=500)
