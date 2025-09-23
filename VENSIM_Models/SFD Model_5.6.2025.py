"""
Python model 'SFD Model_5.6.2025.py'
Translated using PySD
"""

from pathlib import Path
import numpy as np

from pysd.py_backend.functions import if_then_else
from pysd.py_backend.statefuls import Integ
from pysd import Component

__pysd_version__ = "3.13.3"

__data = {"scope": None, "time": lambda: 0}

_root = Path(__file__).parent


component = Component()

#######################################################################
#                          CONTROL VARIABLES                          #
#######################################################################

_control_vars = {
    "initial_time": lambda: 0,
    "final_time": lambda: 60,
    "time_step": lambda: 1,
    "saveper": lambda: time_step(),
}


def _init_outer_references(data):
    for key in data:
        __data[key] = data[key]


@component.add(name="Time")
def time():
    """
    Current time of the model.
    """
    return __data["time"]()


@component.add(
    name="FINAL TIME", units="Month", comp_type="Constant", comp_subtype="Normal"
)
def final_time():
    """
    The final time for the simulation.
    """
    return __data["time"].final_time()


@component.add(
    name="INITIAL TIME", units="Month", comp_type="Constant", comp_subtype="Normal"
)
def initial_time():
    """
    The initial time for the simulation.
    """
    return __data["time"].initial_time()


@component.add(
    name="SAVEPER",
    units="Month",
    limits=(0.0, np.nan),
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time_step": 1},
)
def saveper():
    """
    The frequency with which output is stored.
    """
    return __data["time"].saveper()


@component.add(
    name="TIME STEP",
    units="Month",
    limits=(0.0, np.nan),
    comp_type="Constant",
    comp_subtype="Normal",
)
def time_step():
    """
    The time step for the simulation.
    """
    return __data["time"].time_step()


#######################################################################
#                           MODEL VARIABLES                           #
#######################################################################


@component.add(
    name="Total Population",
    units="Persons/Month",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "tsis": 1,
        "movement_actors": 1,
        "extremist_actors": 1,
        "violent_actors": 1,
    },
)
def total_population():
    return tsis() + movement_actors() + extremist_actors() + violent_actors()


@component.add(
    name="Scaling Factor",
    units="Persons/Month",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"total_population": 2, "total_population_cap": 2},
)
def scaling_factor():
    return if_then_else(
        total_population() > total_population_cap(),
        lambda: total_population_cap() / total_population(),
        lambda: 1,
    )


@component.add(
    name="TOTAL POPULATION CAP",
    units="Persons",
    comp_type="Constant",
    comp_subtype="Normal",
)
def total_population_cap():
    return 10000


@component.add(
    name="Violent Actors",
    units="Persons",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_violent_actors": 1},
    other_deps={
        "_integ_violent_actors": {
            "initial": {},
            "step": {"radicalization": 1, "death_and_incarceration": 1},
        }
    },
)
def violent_actors():
    return _integ_violent_actors()


_integ_violent_actors = Integ(
    lambda: radicalization() - death_and_incarceration(),
    lambda: 5,
    "_integ_violent_actors",
)


@component.add(
    name="Demobilization Rate",
    units="1/Month",
    comp_type="Constant",
    comp_subtype="Normal",
)
def demobilization_rate():
    return 0.94872


@component.add(
    name="Disenfranchisement",
    units="Persons/Month",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"extremist_actors": 1, "disenfranchisement_rate": 1},
)
def disenfranchisement():
    return extremist_actors() * disenfranchisement_rate()


@component.add(
    name="Disenfranchisement Rate",
    units="1/Month",
    comp_type="Constant",
    comp_subtype="Normal",
)
def disenfranchisement_rate():
    return 0.9


@component.add(
    name="Disengagement",
    units="Persons/Month",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"tsis": 1, "disengagement_rate": 1},
)
def disengagement():
    return tsis() * disengagement_rate()


@component.add(
    name="Death and Incarceration",
    units="Persons/Month",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"violent_actors": 1, "death_and_incarceration_rate": 1},
)
def death_and_incarceration():
    return violent_actors() * death_and_incarceration_rate()


@component.add(
    name="Death and Incarceration Rate",
    units="1/Month",
    comp_type="Constant",
    comp_subtype="Normal",
)
def death_and_incarceration_rate():
    return 1


@component.add(
    name="Movement Actors",
    units="Persons",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_movement_actors": 1},
    other_deps={
        "_integ_movement_actors": {
            "initial": {},
            "step": {"mobilization": 1, "demobilization": 1, "escalation": 1},
        }
    },
)
def movement_actors():
    return _integ_movement_actors()


_integ_movement_actors = Integ(
    lambda: mobilization() - demobilization() - escalation(),
    lambda: 975,
    "_integ_movement_actors",
)


@component.add(
    name="Demobilization",
    units="Persons/Month",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"movement_actors": 1, "demobilization_rate": 1},
)
def demobilization():
    return movement_actors() * demobilization_rate()


@component.add(
    name="TSIs",
    units="Persons",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_tsis": 1},
    other_deps={
        "_integ_tsis": {
            "initial": {},
            "step": {"engagement": 1, "disengagement": 1, "mobilization": 1},
        }
    },
)
def tsis():
    return _integ_tsis()


_integ_tsis = Integ(
    lambda: engagement() - disengagement() - mobilization(), lambda: 8970, "_integ_tsis"
)


@component.add(
    name="Engagement",
    units="Persons/Month",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "extremist_actors": 1,
        "online_recruitment_rate": 1,
        "scaling_factor": 1,
    },
)
def engagement():
    return extremist_actors() * online_recruitment_rate() * scaling_factor()


@component.add(
    name="Disengagement Rate",
    units="1/Month",
    comp_type="Constant",
    comp_subtype="Normal",
)
def disengagement_rate():
    return 0.891305


@component.add(
    name="Online Recruitment Rate",
    units="1/Month",
    comp_type="Constant",
    comp_subtype="Normal",
)
def online_recruitment_rate():
    return 179.4


@component.add(
    name="Extremist Actors",
    units="Persons",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_extremist_actors": 1},
    other_deps={
        "_integ_extremist_actors": {
            "initial": {},
            "step": {
                "escalation": 1,
                "nontraditional_susceptible_individual": 1,
                "disenfranchisement": 1,
                "radicalization": 1,
            },
        }
    },
)
def extremist_actors():
    return _integ_extremist_actors()


_integ_extremist_actors = Integ(
    lambda: (escalation() + nontraditional_susceptible_individual())
    - disenfranchisement()
    - radicalization(),
    lambda: 50,
    "_integ_extremist_actors",
)


@component.add(
    name="Active Surveillance",
    units="1/Month",
    comp_type="Constant",
    comp_subtype="Normal",
)
def active_surveillance():
    return 1


@component.add(
    name="Real World Event",
    units="Persons/Month",
    comp_type="Constant",
    comp_subtype="Normal",
)
def real_world_event():
    return 1


@component.add(
    name="DeEscalation Efforts",
    units="1/Month",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"active_surveillance": 1},
)
def deescalation_efforts():
    return 0.01 * active_surveillance()


@component.add(
    name="Law enforcement",
    units="1/Month",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"active_surveillance": 1},
)
def law_enforcement():
    return 0.16128 * active_surveillance()


@component.add(
    name="Radicalization",
    units="Persons/Month",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "extremist_actors": 1,
        "law_enforcement": 1,
        "controlled_isolation": 1,
        "scaling_factor": 1,
    },
)
def radicalization():
    return (
        extremist_actors()
        * (law_enforcement() - controlled_isolation())
        * scaling_factor()
    )


@component.add(
    name="Media Narrative Spin",
    units="Month",
    comp_type="Constant",
    comp_subtype="Normal",
)
def media_narrative_spin():
    return 1


@component.add(
    name="Controlled Isolation",
    units="1/Month",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "controlled_narrative": 1,
        "ingroup_affirmation": 1,
        "multimedia_branding": 1,
        "outgroup_disenfranchisement": 1,
        "perception_of_crisis": 1,
    },
)
def controlled_isolation():
    return (
        controlled_narrative()
        + ingroup_affirmation()
        + multimedia_branding()
        + outgroup_disenfranchisement()
    ) + perception_of_crisis()


@component.add(
    name="Perception of Crisis",
    units="1/Month",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"real_world_event": 1, "media_narrative_spin": 1},
)
def perception_of_crisis():
    return (real_world_event() * media_narrative_spin()) * 0.01


@component.add(
    name="Personal Isolation",
    units="1/Month",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "absence_of_role_model_mentor": 1,
        "access_to_social_resources": 1,
        "adversarial_environment": 1,
        "household_instability": 1,
        "mental_cognitive_diversity": 1,
        "perception_of_crisis": 1,
    },
)
def personal_isolation():
    return (
        absence_of_role_model_mentor()
        + access_to_social_resources()
        + adversarial_environment()
        + household_instability()
        + mental_cognitive_diversity()
    ) + perception_of_crisis()


@component.add(
    name="Escalation",
    units="Persons/Month",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "movement_actors": 1,
        "deescalation_efforts": 1,
        "controlled_isolation": 1,
        "scaling_factor": 1,
    },
)
def escalation():
    return (
        movement_actors()
        * (controlled_isolation() - deescalation_efforts())
        * scaling_factor()
    )


@component.add(
    name="Mobilization",
    units="Persons/Month",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "tsis": 1,
        "deescalation_efforts": 1,
        "personal_isolation": 1,
        "scaling_factor": 1,
    },
)
def mobilization():
    return tsis() * (personal_isolation() - deescalation_efforts()) * scaling_factor()


@component.add(
    name="Absence of Role Model Mentor",
    units="1/Month",
    comp_type="Constant",
    comp_subtype="Normal",
)
def absence_of_role_model_mentor():
    return 0.036958


@component.add(
    name="Access to Social Resources",
    units="1/Month",
    comp_type="Constant",
    comp_subtype="Normal",
)
def access_to_social_resources():
    return 0.014131


@component.add(
    name="Adversarial Environment",
    units="1/Month",
    comp_type="Constant",
    comp_subtype="Normal",
)
def adversarial_environment():
    return 0.028262


@component.add(
    name="Controlled Narrative",
    units="1/Month",
    comp_type="Constant",
    comp_subtype="Normal",
)
def controlled_narrative():
    return 0.010256


@component.add(
    name="Household Instability",
    units="1/Month",
    comp_type="Constant",
    comp_subtype="Normal",
)
def household_instability():
    return 0.020653


@component.add(
    name="Ingroup Affirmation",
    units="1/Month",
    comp_type="Constant",
    comp_subtype="Normal",
)
def ingroup_affirmation():
    return 0.020512


@component.add(
    name="Mental Cognitive Diversity",
    units="1/Month",
    comp_type="Constant",
    comp_subtype="Normal",
)
def mental_cognitive_diversity():
    return 0.008696


@component.add(
    name="Multimedia Branding",
    units="1/Month",
    comp_type="Constant",
    comp_subtype="Normal",
)
def multimedia_branding():
    return 0.005128


@component.add(
    name="Nontraditional Susceptible Individual",
    units="Persons/Month",
    comp_type="Constant",
    comp_subtype="Normal",
)
def nontraditional_susceptible_individual():
    return 0


@component.add(
    name="Outgroup Disenfranchisement",
    units="1/Month",
    comp_type="Constant",
    comp_subtype="Normal",
)
def outgroup_disenfranchisement():
    return 0.015384
