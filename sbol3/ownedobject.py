import posixpath
from typing import Union, Any, List, Optional, Dict

import rdflib

from . import *


class OwnedObjectPropertyMixin:

    def from_user(self, value: Any) -> rdflib.Literal:
        if not isinstance(value, SBOLObject):
            raise TypeError(f'Expecting SBOLObject, got {type(value)}')
        return value

    def to_user(self, value: Any) -> str:
        return value

    def _storage(self) -> Dict[str, list]:
        return self.property_owner.owned_objects


class OwnedObjectSingletonProperty(OwnedObjectPropertyMixin, SingletonProperty):

    def __init__(self, property_owner: Any, property_uri: str,
                 lower_bound: int, upper_bound: int,
                 validation_rules: Optional[List] = None,
                 initial_value: Optional[str] = None):
        super().__init__(property_owner, property_uri,
                         lower_bound, upper_bound, validation_rules)
        if initial_value:
            self.set(initial_value)


class OwnedObjectListProperty(OwnedObjectPropertyMixin, ListProperty):

    def __init__(self, property_owner: Any, property_uri: str,
                 lower_bound: int, upper_bound: int,
                 validation_rules: Optional[List] = None,
                 initial_value: Optional[str] = None):
        super().__init__(property_owner, property_uri,
                         lower_bound, upper_bound, validation_rules)
        if initial_value:
            self.set(initial_value)

    def item_added(self, item: Any) -> None:
        if not self.property_owner.identity_is_url():
            return
        if not item.display_id:
            raise ValueError(f'Item {item} does not have a display_id')
        new_url = posixpath.join(self.property_owner.identity, item.display_id)
        for sibling in self._storage()[self.property_uri]:
            if sibling == item:
                continue
            if sibling.identity == new_url:
                raise ValidationError(f'Duplicate URI: {new_url}')
        item._identity = new_url


def OwnedObject(property_owner: Any, property_uri: str,
                lower_bound: int, upper_bound: Union[int, float],
                validation_rules: Optional[List] = None,
                initial_value: Optional[Union[str, List[str]]] = None) -> Property:
    if upper_bound == 1:
        return OwnedObjectSingletonProperty(property_owner, property_uri,
                                            lower_bound, upper_bound,
                                            validation_rules, initial_value)
    return OwnedObjectListProperty(property_owner, property_uri,
                                   lower_bound, upper_bound,
                                   validation_rules, initial_value)